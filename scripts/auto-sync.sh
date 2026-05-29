#!/usr/bin/env bash
# Runs full backup then auto git commit/push — intended for cron every 30 minutes.
#
# Usage:
#   bash scripts/auto-sync.sh
# Cron (install via scripts/install-auto-sync-cron.sh):
#   */30 * * * * bash /home/mrram/srtapp/scripts/auto-sync.sh >> ~/srtapp-backups/auto-sync.log 2>&1

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${BACKUP_ROOT:-$HOME/srtapp-backups}"

# Auto-sync guard: require a user-controlled enable file to actually run backups.
# This prevents cron from taking backups unless the user explicitly enables them.
# Create the file to enable: `touch ~/.srtapp-auto-backup-enabled`
ENABLE_FILE="${AUTO_SYNC_ENABLE_FILE:-$HOME/.srtapp-auto-backup-enabled}"
if [[ ! -f "$ENABLE_FILE" ]]; then
  mkdir -p "$LOG_DIR"
  log "Auto-sync disabled — create $ENABLE_FILE to enable scheduled backups."
  exit 0
fi

log() { printf '[auto-sync] %s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }

mkdir -p "$LOG_DIR"
log "=== Scheduled backup + git push started ==="

BACKUP_OK=0
if bash "$REPO_ROOT/scripts/backup-srtapp.sh"; then
  BACKUP_OK=1
  log "Backup finished OK"
else
  log "WARN: backup script exited with error — continuing to git push"
fi

GIT_OK=0
if bash "$REPO_ROOT/scripts/auto-git-push.sh"; then
  GIT_OK=1
  log "Git push finished OK"
else
  log "WARN: auto-git-push exited with error"
fi

log "=== Done (backup=$BACKUP_OK git=$GIT_OK) ==="

if [[ "$BACKUP_OK" -eq 1 && "$GIT_OK" -eq 1 ]]; then
  exit 0
fi
exit 1

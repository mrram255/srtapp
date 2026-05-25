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

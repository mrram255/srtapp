#!/usr/bin/env bash
# Install or refresh the 30-minute auto backup + git push cron job.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CRON_LINE="*/30 * * * * bash $REPO_ROOT/scripts/auto-sync.sh >> \$HOME/srtapp-backups/auto-sync.log 2>&1"
MARKER="# srtapp-auto-sync"

mkdir -p "$HOME/srtapp-backups"
chmod +x "$REPO_ROOT/scripts/auto-sync.sh" \
  "$REPO_ROOT/scripts/auto-git-push.sh" \
  "$REPO_ROOT/scripts/backup-srtapp.sh"

EXISTING="$(crontab -l 2>/dev/null || true)"
if echo "$EXISTING" | grep -Fq "$MARKER"; then
  EXISTING="$(echo "$EXISTING" | grep -Fv "$MARKER" | grep -Fv "scripts/auto-sync.sh" || true)"
fi

{
  echo "$EXISTING" | sed '/^$/d'
  echo "$MARKER"
  echo "$CRON_LINE"
} | crontab -

echo "Cron installed — runs every 30 minutes:"
crontab -l | grep -A1 "$MARKER"

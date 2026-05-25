#!/usr/bin/env bash
# Commit and push local changes every cron run (skips when nothing to push).
# Never stages .env files or other secrets ignored by .gitignore.
#
# Usage:
#   bash scripts/auto-git-push.sh
# Logs append to $BACKUP_ROOT/auto-git.log when run from cron.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${BACKUP_ROOT:-$HOME/srtapp-backups}"
BRANCH="${GIT_BRANCH:-main}"
REMOTE="${GIT_REMOTE:-origin}"

log() { printf '[auto-git] %s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }

cd "$REPO_ROOT"
mkdir -p "$LOG_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  log "ERROR: not a git repository ($REPO_ROOT)"
  exit 1
fi

# Drop tracked env files from index so .gitignore can protect them.
for envfile in .env backend/.env frontend/.env.local mobile/.env; do
  if git ls-files --error-unmatch "$envfile" >/dev/null 2>&1; then
    git rm --cached -f "$envfile" >/dev/null 2>&1 || true
    log "Removed from git index (kept on disk): $envfile"
  fi
done

# Stage everything except explicit secret paths (belt + suspenders).
git add -A -- \
  . \
  ':!.env' \
  ':!backend/.env' \
  ':!frontend/.env.local' \
  ':!mobile/.env' \
  ':!**/srtapp-backups' \
  ':!backend/venv' \
  ':!backend/media' \
  2>/dev/null || git add -A

if git diff --cached --quiet; then
  log "No changes to commit — skipping push"
  exit 0
fi

MSG="auto-backup: $(date '+%Y-%m-%d %H:%M')"
git commit -m "$MSG" --no-gpg-sign
log "Committed: $MSG"

CURRENT_BRANCH="$(git branch --show-current)"
TARGET="${CURRENT_BRANCH:-$BRANCH}"

if ! git rev-parse --verify "$REMOTE/$TARGET" >/dev/null 2>&1; then
  log "Pushing new branch to $REMOTE ($TARGET)..."
  git push -u "$REMOTE" "$TARGET"
else
  log "Pushing to $REMOTE ($TARGET)..."
  git push "$REMOTE" "$TARGET"
fi

log "Push complete"

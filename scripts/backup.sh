#!/usr/bin/env bash
# Database backup helper — run on host with pg_dump available.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="${ROOT}/backups"
mkdir -p "$BACKUP_DIR"
STAMP=$(date +%Y%m%d_%H%M%S)
FILE="${BACKUP_DIR}/srtapp_${STAMP}.sql"

cd "${ROOT}/backend"
python manage.py backup_database 2>/dev/null || true

if command -v pg_dump >/dev/null 2>&1; then
  : "${DB_NAME:=srtapp_db}"
  : "${DB_USER:=srtapp_user}"
  : "${DB_HOST:=localhost}"
  pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" > "$FILE"
  echo "Backup written to $FILE"
else
  echo "pg_dump not found. Use: docker compose exec db pg_dump -U srtapp_user srtapp_db > $FILE"
fi

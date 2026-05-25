#!/usr/bin/env bash
# Full SRTAPP backup: project source, .env files, PostgreSQL, media, optional Docker data.
#
# Usage:
#   bash scripts/backup-srtapp.sh              # recommended (slim: skips node_modules/venv/.next)
#   bash scripts/backup-srtapp.sh --full       # includes node_modules, venv, .next (very large)
#   BACKUP_ROOT=/mnt/usb bash scripts/backup-srtapp.sh
#
# Output: $BACKUP_ROOT/srtapp_YYYYMMDD_HHMMSS/

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_ROOT="${BACKUP_ROOT:-$HOME/srtapp-backups}"
OUT="$BACKUP_ROOT/srtapp_$STAMP"
FULL=0

for arg in "$@"; do
  case "$arg" in
    --full) FULL=1 ;;
    -h|--help)
      sed -n '1,12p' "$0"
      exit 0
      ;;
  esac
done

mkdir -p "$OUT"/{database,env,media,docker,project}

log() { printf '[backup] %s\n' "$*"; }

# ── Load DB creds (backend/.env → repo .env → defaults) ──
DB_NAME="${DB_NAME:-srtapp_db}"
DB_USER="${DB_USER:-srtapp_user}"
DB_PASSWORD="${DB_PASSWORD:-srtapp_pass}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

if [[ -f "$REPO_ROOT/backend/.env" ]]; then
  # shellcheck disable=SC1091
  set -a
  # Only export DB_* lines to avoid breaking on special chars in other vars
  while IFS= read -r line; do
    [[ "$line" =~ ^DB_ ]] || continue
    [[ "$line" =~ ^# ]] && continue
    export "$line" 2>/dev/null || true
  done < <(grep -E '^DB_' "$REPO_ROOT/backend/.env" || true)
  set +a
fi

if [[ -f "$REPO_ROOT/.env" ]]; then
  while IFS= read -r line; do
    [[ "$line" =~ ^DB_ ]] || continue
    [[ "$line" =~ ^# ]] && continue
    export "$line" 2>/dev/null || true
  done < <(grep -E '^DB_' "$REPO_ROOT/.env" || true)
fi

log "Backup folder: $OUT"

# ── 1) Environment files (secrets — keep backup private) ──
log "Copying .env files..."
for f in \
  "$REPO_ROOT/.env" \
  "$REPO_ROOT/.env.example" \
  "$REPO_ROOT/backend/.env" \
  "$REPO_ROOT/backend/.env.example" \
  "$REPO_ROOT/frontend/.env.local" \
  "$REPO_ROOT/frontend/.env.local.example" \
  "$REPO_ROOT/mobile/.env" \
  "$REPO_ROOT/mobile/.env.example"
do
  if [[ -f "$f" ]]; then
    rel="${f#$REPO_ROOT/}"
    mkdir -p "$OUT/env/$(dirname "$rel")"
    cp -a "$f" "$OUT/env/$rel"
  fi
done

# ── 2) PostgreSQL dump ──
PG_DUMP_OK=0
if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx 'srtapp-db'; then
  log "PostgreSQL: docker exec srtapp-db pg_dump..."
  docker exec -e PGPASSWORD="$DB_PASSWORD" srtapp-db \
    pg_dump -U "$DB_USER" -d "$DB_NAME" --no-owner --no-acl \
    > "$OUT/database/postgres_${DB_NAME}.sql"
  PG_DUMP_OK=1
elif command -v pg_dump >/dev/null 2>&1; then
  log "PostgreSQL: pg_dump via host ($DB_HOST:$DB_PORT)..."
  PGPASSWORD="$DB_PASSWORD" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --no-owner --no-acl > "$OUT/database/postgres_${DB_NAME}.sql" && PG_DUMP_OK=1 || true
fi

if [[ "$PG_DUMP_OK" -eq 1 ]]; then
  gzip -f "$OUT/database/postgres_${DB_NAME}.sql"
  log "PostgreSQL dump: database/postgres_${DB_NAME}.sql.gz"
else
  log "WARN: PostgreSQL dump skipped (container srtapp-db not running and pg_dump failed)."
  echo "PostgreSQL dump failed or DB not reachable at backup time." > "$OUT/database/README.txt"
fi

# ── 3) Django media (uploads on host) ──
if [[ -d "$REPO_ROOT/backend/media" ]]; then
  log "Copying backend/media..."
  rsync -a "$REPO_ROOT/backend/media/" "$OUT/media/backend_media/"
fi

# ── 4) Optional Docker volume snapshots (Redis AOF, MinIO, Meilisearch) ──
if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx 'srtapp-redis'; then
  log "Redis: saving RDB snapshot..."
  docker exec srtapp-redis redis-cli -a "${REDIS_PASSWORD:-redis_pass}" SAVE >/dev/null 2>&1 || true
  docker cp srtapp-redis:/data/dump.rdb "$OUT/docker/redis_dump.rdb" 2>/dev/null || \
    log "WARN: redis dump.rdb copy failed (may use AOF only)."
fi

if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx 'srtapp-minio'; then
  log "MinIO: copying /data from container..."
  MINIO_TMP="$OUT/docker/_minio_data"
  rm -rf "$MINIO_TMP"
  mkdir -p "$MINIO_TMP"
  if docker cp srtapp-minio:/data/. "$MINIO_TMP/" 2>/dev/null; then
    tar -cf "$OUT/docker/minio_data.tar" -C "$MINIO_TMP" .
    rm -rf "$MINIO_TMP"
    log "MinIO archive: docker/minio_data.tar"
  else
    rm -rf "$MINIO_TMP"
    log "WARN: MinIO archive failed (docker cp)."
  fi
fi

if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx 'srtapp-meilisearch'; then
  log "Meilisearch: archiving /meili_data..."
  docker exec srtapp-meilisearch sh -c 'cd /meili_data && tar cf - .' > "$OUT/docker/meilisearch_data.tar" 2>/dev/null || \
    log "WARN: Meilisearch archive failed."
fi

# ── 5) Project source tree ──
RSYNC_EXCLUDES=(
  --exclude '.git'
  --exclude '**/node_modules'
  --exclude '**/.expo'
  --exclude '**/.next'
  --exclude '**/venv'
  --exclude '**/__pycache__'
  --exclude '**/.pytest_cache'
  --exclude '**/mobile/_export_smoke'
  --exclude 'backend/staticfiles'
  --exclude 'backend/db.sqlite3'
)

if [[ "$FULL" -eq 1 ]]; then
  RSYNC_EXCLUDES=(
    --exclude '.git'
    --exclude 'backend/db.sqlite3'
  )
  log "Project: rsync FULL (includes node_modules, venv, .next — large)..."
else
  log "Project: rsync slim (excludes node_modules, venv, .next)..."
fi

rsync -a "${RSYNC_EXCLUDES[@]}" "$REPO_ROOT/" "$OUT/project/srtapp/"

# ── 6) Manifest ──
{
  echo "SRTAPP backup"
  echo "Created: $(date -Iseconds)"
  echo "Host: $(hostname)"
  echo "Repo: $REPO_ROOT"
  echo "Mode: $([[ "$FULL" -eq 1 ]] && echo full || echo slim)"
  echo "Postgres dump: $([[ "$PG_DUMP_OK" -eq 1 ]] && echo yes || echo no)"
  echo ""
  echo "Restore hints:"
  echo "  1. Unpack/copy project/ back to ~/srtapp"
  echo "  2. Restore env/ files to matching paths"
  echo "  3. gunzip database/*.sql.gz && psql/docker exec -i ... < postgres_srtapp_db.sql"
  echo "  4. rsync media/backend_media/ -> backend/media/"
} > "$OUT/MANIFEST.txt"

ARCHIVE="$BACKUP_ROOT/srtapp_${STAMP}.tar.gz"
log "Creating archive: $ARCHIVE"
tar -czf "$ARCHIVE" -C "$BACKUP_ROOT" "srtapp_$STAMP"

SIZE="$(du -sh "$ARCHIVE" | cut -f1)"
log "Done. Folder: $OUT"
log "Archive: $ARCHIVE ($SIZE)"
log "Keep backup private — contains .env and database."

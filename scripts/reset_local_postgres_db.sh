#!/usr/bin/env bash
# Drop and recreate the local Postgres DB used by docker-compose (fixes
# InconsistentMigrationHistory on dev machines). ALL DATA in srtapp_db is lost.
#
# Usage (from repo root):
#   bash scripts/reset_local_postgres_db.sh
#   cd backend && source venv/bin/activate && python manage.py migrate

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ROOT/.env" 2>/dev/null || true
  set +a
fi
DB_PASS="${DB_PASSWORD:-srtapp_pass}"
CONTAINER="${POSTGRES_CONTAINER_NAME:-srtapp-db}"

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "Container '$CONTAINER' is not running. Start infra first:"
  echo "  bash scripts/start-local-deps.sh"
  exit 1
fi

echo "Dropping database srtapp_db inside $CONTAINER (dev data erased) …"

docker exec -i -e PGPASSWORD="$DB_PASS" "$CONTAINER" psql -U srtapp_user -d postgres <<-SQL
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'srtapp_db' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS srtapp_db;
CREATE DATABASE srtapp_db OWNER srtapp_user;
SQL

echo ""
echo "Done. Run migrations:"
echo "  cd backend && source venv/bin/activate && python manage.py migrate"

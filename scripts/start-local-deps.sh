#!/usr/bin/env bash
# Start Postgres, Redis, MinIO, Meilisearch in Docker — run Django / Next / Expo on your machine against these ports.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found — install Docker, or install Postgres + Redis manually and set backend/.env."
  exit 1
fi

# Docker Compose v2 only (`docker compose` plugin). Compose v1 (Python `docker-compose` 1.29.x)
# throws KeyError: 'ContainerConfig' on modern Docker when recreating containers.
if docker compose version >/dev/null 2>&1; then
  compose() { docker compose "$@"; }
else
  cat << EOF
❌ Compose v2 is required ('docker compose' command not found).

  This avoids the obsolete Python docker-compose 1.x error:
    KeyError: 'ContainerConfig'

  If apt fails with "Unable to locate package docker-compose-plugin", Ubuntu often
  does not have Docker's official repository — install the CLI plugin manually:

    bash scripts/install-docker-compose-v2.sh

  Or add Docker's apt repo then: sudo apt-get install docker-compose-plugin
    https://docs.docker.com/engine/install/ubuntu/

  Docker Desktop (Windows): enable WSL2 integration for this distro,
  docker engine running, then: docker compose version

EOF
  exit 1
fi

if [[ ! -f "$ROOT/.env" ]]; then
  echo "Hint: cp .env.example .env  # optional; Compose uses defaults inside docker-compose.yml if unset."
fi

echo "Starting: db redis minio meilisearch …"
compose up -d db redis minio meilisearch

# Show real values: repo-root .env is what Compose reads for substituting ${VAR:-default}
if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ROOT/.env" 2>/dev/null || true
  set +a
fi
DB_P="${DB_PASSWORD:-srtapp_pass}"
REDIS_P="${REDIS_PASSWORD:-redis_pass}"
MEILI_K="${MEILISEARCH_API_KEY:-master_key}"

echo ""
echo "Services:"
echo "  Postgres      localhost:5432   (DB srtapp_db / user srtapp_user / pass $DB_P)"
echo "  Redis         localhost:6379   (password $REDIS_P)"
echo "  MinIO         localhost:9000   (console :9001)"
echo "  Meilisearch   localhost:7700   (MEILI_MASTER_KEY $MEILI_K)"
echo ""
echo "Next steps (match backend/.env to the passwords above if you use Docker DB/Redis):"
echo "  1) Backend: cd backend && source venv/bin/activate && python manage.py migrate && python manage.py runserver"
echo "  2) Frontend: cd frontend && npm install && cp -n .env.local.example .env.local && npm run dev"
echo "  3) Mobile:   cd mobile && npm install && cp -n .env.example .env && npx expo start"
echo ""

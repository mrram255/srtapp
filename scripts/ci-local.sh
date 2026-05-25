#!/usr/bin/env bash
# Run backend tests + Django check + frontend lint (local CI smoke).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== Repo structure verify =="
python3 "$ROOT/scripts/verify_project_structure.py"

echo "== Backend pytest =="
(cd "$ROOT/backend" && ./venv/bin/pytest -q)

echo "== Django check (development settings; uses env secrets if set) =="
export DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-django-dev-secret-key-at-least-fifty-characters-long-xxxxx}"
export JWT_SECRET_KEY="${JWT_SECRET_KEY:-jwt-dev-secret-key-at-least-fifty-characters-long-xxxxx}"
(cd "$ROOT/backend" && ./venv/bin/python manage.py check)

echo "== Frontend ESLint =="
(cd "$ROOT/frontend" && npm run lint)

echo "Done."

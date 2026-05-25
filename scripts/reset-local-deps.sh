#!/usr/bin/env bash
# Tear down infra containers for this compose project + remove orphaned srtapp-* boxes
# (fixes v1-era names like 08f9de4cc953_srtapp-minio blocking docker compose up).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if docker compose version >/dev/null 2>&1; then
  compose() { docker compose "$@"; }
else
  echo "docker compose not found"; exit 1
fi

echo "Stopping project stack (compose down --remove-orphans) …"
compose down --remove-orphans 2>/dev/null || true

echo "Removing containers whose names mention srtapp …"
docker ps -aq --filter name=srtapp | while read -r id; do
  [[ -n "$id" ]] || continue
  docker rm -f "$id" >/dev/null 2>&1 && echo "  removed $id" || true
done

echo "Done. Next: bash scripts/start-local-deps.sh"

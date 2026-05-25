#!/usr/bin/env bash
# Install Docker Compose v2 as a user-level CLI plugin (~/.docker/cli-plugins/docker-compose).
# Use this when Ubuntu apt cannot install docker-compose-plugin (no Docker CE apt repo).

set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "docker CLI not found. Install Docker first."
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  echo "Already OK:"
  docker compose version
  exit 0
fi

ARCH="$(uname -m)"
case "$ARCH" in
  x86_64)  BIN="docker-compose-linux-x86_64" ;;
  aarch64) BIN="docker-compose-linux-aarch64" ;;
  arm64)   BIN="docker-compose-linux-aarch64" ;;
  *)
    echo "Unsupported CPU arch: $ARCH (need x86_64 or aarch64)"
    exit 1 ;;
esac

DC="${DOCKER_CONFIG:-$HOME/.docker}"
PLUGIN_DIR="$DC/cli-plugins"
mkdir -p "$PLUGIN_DIR"

URL="https://github.com/docker/compose/releases/latest/download/$BIN"
OUT="$PLUGIN_DIR/docker-compose"

echo "Downloading Compose v2 → $OUT"
curl -fSL "$URL" -o "$OUT"
chmod +x "$OUT"

echo ""
docker compose version
echo ""
echo "Done. Run: bash scripts/start-local-deps.sh"

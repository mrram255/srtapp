#!/usr/bin/env bash
# Example: POST login against local Django (requires runserver on :8000).
# Usage:
#   API_EMAIL=you@example.com API_PASSWORD='your-strong-password' bash scripts/example_api_login.sh
set -euo pipefail

EMAIL="${API_EMAIL:?Set API_EMAIL}"
PASS="${API_PASSWORD:?Set API_PASSWORD}"
URL="${API_BASE:-http://127.0.0.1:8000}"

curl -sS -X POST "${URL}/api/v1/auth/login/" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASS}\"}" | python3 -m json.tool

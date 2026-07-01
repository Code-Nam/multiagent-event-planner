#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

# Load .env
if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"
API_PORT="${API_PORT:-8001}"
WEBAPP_PORT="${WEBAPP_PORT:-5174}"
VITE_API_BASE="${VITE_API_BASE:-http://localhost:$API_PORT}"

API_PID=""
WEBAPP_PID=""

cleanup() {
  echo ""
  [[ -n "$API_PID" ]]    && kill "$API_PID"    2>/dev/null || true
  [[ -n "$WEBAPP_PID" ]] && kill "$WEBAPP_PID" 2>/dev/null || true
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "CLAUDE_DIR : $CLAUDE_DIR"
echo "API        : http://localhost:$API_PORT"
echo "Webapp     : http://localhost:$WEBAPP_PORT"
echo ""

CLAUDE_DIR="$CLAUDE_DIR" \
  "$ROOT/api/venv/bin/uvicorn" api.main:app \
  --host 0.0.0.0 --port "$API_PORT" \
  --reload &
API_PID=$!

VITE_API_BASE="$VITE_API_BASE" \
  npm --prefix "$ROOT/webapp" run dev -- --port "$WEBAPP_PORT" &
WEBAPP_PID=$!

wait

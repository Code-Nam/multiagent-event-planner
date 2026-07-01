#!/usr/bin/env bash
# MCP wrapper: loads GOOGLE_SERVICE_ACCOUNT_KEY from file if env var not set.
# Place your service account JSON at scripts/gdrive_service_account.json

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SA_FILE="$SCRIPT_DIR/gdrive_service_account.json"

if [ -z "$GOOGLE_SERVICE_ACCOUNT_KEY" ] && [ -f "$SA_FILE" ]; then
  export GOOGLE_SERVICE_ACCOUNT_KEY="$(cat "$SA_FILE")"
fi

if [ -z "$GOOGLE_SERVICE_ACCOUNT_KEY" ]; then
  echo "ERROR: GOOGLE_SERVICE_ACCOUNT_KEY not set and $SA_FILE not found." >&2
  echo "Create a service account at console.cloud.google.com and save the JSON key as scripts/gdrive_service_account.json" >&2
  exit 1
fi

exec npx -y mcp-google-drive "$@"

#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONTEXT="$SCRIPT_DIR/../../event-context.md"
SEP="──────────────────────────────────────────────"

if grep -q '\[TBD\]' "$CONTEXT" 2>/dev/null; then
  printf '\n%s\n' "$SEP"
  printf '  AGEVP — No event configured\n'
  printf '%s\n' "$SEP"
  printf '  Run session-init to begin\n'
  printf '%s\n\n' "$SEP"
else
  NAME=$(grep '^\*\*Name:\*\*'         "$CONTEXT" | sed 's/\*\*Name:\*\* //')
  DATE=$(grep '^\*\*Date:\*\*'         "$CONTEXT" | sed 's/\*\*Date:\*\* //')
  TYPE=$(grep '^\*\*Type:\*\*'         "$CONTEXT" | sed 's/\*\*Type:\*\* //')
  BUDGET=$(grep '^\*\*Fixed budget:\*\*' "$CONTEXT" | sed 's/\*\*Fixed budget:\*\* //')
  LEAD=$(grep '^\*\*Event lead:\*\*'   "$CONTEXT" | sed 's/\*\*Event lead:\*\* //')

  printf '\n%s\n' "$SEP"
  printf '  AGEVP — Event Active\n'
  printf '%s\n' "$SEP"
  printf '  Event  : %s\n' "$NAME"
  printf '  Date   : %s\n' "$DATE"
  printf '  Type   : %s\n' "$TYPE"
  printf '  Budget : %s\n' "$BUDGET"
  printf '  Lead   : %s\n' "$LEAD"
  printf '%s\n' "$SEP"
  printf '  session-init · venue-scout · info-compiler · budget-validator · event-planner\n'
  printf '  email-drafter · doc-generator · claude-reviewer · doc-updater · py-dev\n'
  printf '  gdrive-uploader · api-dev · webapp-dev\n'
  printf '%s\n\n' "$SEP"
fi

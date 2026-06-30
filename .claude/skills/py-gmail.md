---
name: py-gmail
description: Create a Gmail API draft from the latest email-drafter output in drafts/. Delegates to py-dev which runs scripts/gmail_draft.py. Reports draft ID to user.
---

Push a Markdown email draft to Gmail as an API draft (not sent).

## Args (optional)

`/py-gmail` → latest draft in drafts/  
`/py-gmail venue_inquiry` → latest draft matching that purpose prefix

## Steps

1. **Check scripts/credentials.json** — if missing, stop immediately:

```
── PY-GMAIL BLOCKED ──────────────────────────────
  Missing: scripts/credentials.json

  Setup:
  1. Go to Google Cloud Console → APIs & Services → Credentials
  2. Create OAuth 2.0 Client ID (Desktop app type)
  3. Download JSON → save as scripts/credentials.json
  4. Enable Gmail API in your project
──────────────────────────────────────────────────
```

2. **Find latest draft** — list `drafts/`, filter by purpose arg if provided, use most recently modified.
3. **Delegate to py-dev** with: task = "Gmail draft", draft path, confirmation credentials.json exists.
4. **Wait for receipt** containing draft ID.
5. **Report:**

```
── PY-GMAIL COMPLETE ─────────────────────────────
  source:   drafts/<file>
  draft ID: <id>
  status:   draft only — not sent
  view at:  https://mail.google.com/#drafts
──────────────────────────────────────────────────
```

## Rules

- Credentials check is mandatory — never skip, never delegate without it.
- Draft only. Never instruct py-dev to send.
- On multiple matches for the same purpose: use most recently modified file.
- First run opens browser for OAuth consent — inform user before delegating.

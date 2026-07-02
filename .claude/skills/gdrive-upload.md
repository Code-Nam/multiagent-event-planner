---
name: gdrive-upload
description: Upload all output/ files to Google Drive under an event-named folder. Delegates to gdrive-uploader which runs scripts/gdrive_upload.py (OAuth2, drive.file scope). Returns folder + per-file links.
---

Upload generated `output/` files to Google Drive.

## Steps

1. Check `output/` contains files — if empty, stop and suggest `/py-run` first.
2. Delegate to the `gdrive-uploader` agent. Pass:
   - Context: `event-context.md` location and current event name (if known)
   - Instruction: upload all files from `output/` to Google Drive
3. Wait for receipt with Drive folder link + per-file links.
4. Report links to user.

## Rules

- First run opens a browser for OAuth consent — inform user before delegating.
- Upload only — never instruct the agent to delete or share Drive files.
- The agent runs `scripts/gdrive_upload.py` from the project root — no absolute paths.

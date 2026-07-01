Delegate to the `gdrive-uploader` agent.

Pass:
- Project root: `/home/codenam/Github/multiagent-event-planner`
- Context: `event-context.md` location and current event name (if known)
- Instruction: upload all files from `output/` to Google Drive

The agent runs `scripts/gdrive_upload.py` (OAuth2) and returns Drive links.

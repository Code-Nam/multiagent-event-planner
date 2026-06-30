---
name: sync-docs
description: Sync README.md, CLAUDE.md routing table, and settings.json to match current agents and skills. Run after adding or removing agents/skills.
---

Update all human-facing documentation to reflect the current Claude config state.

## When to use

- After adding new agents or skills
- After renaming or removing agents or skills
- After `/claude-review` flags doc inconsistencies (🟡 Medium issues)

## Steps

1. Delegate to `doc-updater` with no additional input — it reads the current config autonomously.
2. Wait for receipt listing all changes made.
3. Show user the receipt.
4. Suggest committing:

```
Suggested commit:
  docs: sync README, CLAUDE.md and settings to current agent/skill set
```

## Rules

- Never trigger if `event-context.md` is blank — no event data should affect docs.
- After doc-updater completes, run `/claude-review` optionally to verify no issues remain.

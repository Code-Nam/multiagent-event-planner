---
name: claude-review
description: Audit all Claude config files (agents, skills, CLAUDE.md, README, settings) and return a prioritised improvement plan. Read-only — no edits.
---

Trigger a full read-only audit of the AGEVP Claude configuration.

## Steps

1. Delegate to `claude-reviewer` with no additional input — it reads the full config autonomously.
2. Wait for the audit report.
3. Present the report to the user verbatim.
4. If issues are found, suggest next actions:
   - 🔴 High → fix manually or via targeted agent delegation
   - 🟡 Medium → run `/sync-docs` if doc inconsistencies, else fix manually
   - 🟢 Low → user decides

## Rules

- Never edit anything based on the report — read-only, present findings only.
- Never filter or summarise the report — show it in full.

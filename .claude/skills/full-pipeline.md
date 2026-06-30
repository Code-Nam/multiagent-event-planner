---
name: full-pipeline
description: Run the full event planning pipeline sequentially: venue-scout → info-compiler → budget-validator → event-planner.
---

Run the full planning pipeline for the current event. Requires `event-context.md` to be populated — if not, run `session-init` first.

## Steps (in order — wait for each to complete before starting next)

1. **Check event-context.md** — if still template (`[TBD]` values), stop and tell user to run `session-init` first.

2. **venue-scout** — delegate with full event context (type, capacity, budget, area, constraints from event-context.md). Wait for receipt.

3. **info-compiler** — delegate with path to venues file from step 2. Wait for receipt.

4. **budget-validator** — delegate. Let it auto-scan drafts/compiled-*.md for venue costs. Wait for receipt.
   - If 🔴 REJECTED: stop pipeline, report to user. Do not continue until user decides.

5. **event-planner** — delegate with event-context.md + planning constraints. Generate all 4 deliverables. Wait for receipt.

## After pipeline completes

Report a summary:

```
── FULL PIPELINE COMPLETE ────────────────────────
  venues found:    <n>  → drafts/venues-*.md
  recommendation:  <venue name>  → drafts/compiled-*.md
  budget status:   ✅ APPROVED / 🔴 REJECTED  → drafts/budget-*.md
  planning:        4 deliverables  → drafts/planning-*.md

  Suggested next steps:
  - /email-drafter: contact selected venue
  - /export: generate official documents
──────────────────────────────────────────────────
```

## Rules

- Sequential only — never run steps in parallel.
- Stop on budget rejection — do not suppress or override without explicit user instruction.
- Pass explicit file paths between each agent delegation — subagents share no memory.

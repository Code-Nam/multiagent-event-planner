---
name: venue-pipeline
description: Run the venue selection sub-pipeline: venue-scout → info-compiler → budget-validator. Stops before operational planning.
---

Run only the venue phase of the full pipeline. Use when venue selection is the current focus and operational planning is not yet needed.

## Steps (sequential — wait for each receipt before next)

1. **Check event-context.md** — if still template, stop and tell user to run `session-init` first.

2. **venue-scout** — delegate with full event context from event-context.md (type, capacity, budget, area, date, constraints). Wait for receipt.

3. **info-compiler** — delegate with:
   - Path to venues file from step 2
   - Budget max from event-context.md
   - Prioritisation: price first, then capacity fit
   Wait for receipt.

4. **budget-validator** — delegate. Let it auto-scan `drafts/compiled-*.md` for venue costs.
   - ✅ APPROVED: continue to summary.
   - 🔴 REJECTED: stop pipeline, report to user. Suggest `/budget-override` or revising the venue selection.

## After pipeline completes

```
── VENUE PIPELINE COMPLETE ───────────────────────
  venues found:    <n>  → drafts/venues-*.md
  recommendation:  <venue name> (€<price>)  → drafts/compiled-*.md
  budget status:   ✅ APPROVED / 🔴 REJECTED  → drafts/budget-*.md

  Suggested next steps:
  - /email-venue: draft inquiry to recommended venue
  - /event-recap: view full planning summary
  - /full-pipeline: continue to operational planning
──────────────────────────────────────────────────
```

## Rules

- Sequential only — never run steps in parallel.
- Always run info-compiler in this pipeline (not optional here — ranking is the point).
- Stop on budget rejection — suggest `/budget-override` if user wants to proceed anyway.
- Pass explicit file paths between delegations — subagents share no memory.

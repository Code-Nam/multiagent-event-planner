---
name: plan-status
description: Show current event planning progress — which pipeline steps are done, which are pending.
---

Read the following files and report planning status:

1. `event-context.md` — check if populated (not all `[TBD]`) or still template
2. `drafts/` — list all files present, grouped by prefix:
   - `venues-*` → venue-scout done
   - `compiled-*` → info-compiler done
   - `budget-*` → budget-validator done
   - `planning-*` → event-planner done
   - email drafts (`venue_inquiry-*`, `sponsor_outreach-*`, etc.) → email-drafter done
3. `doc-content/` — list JSON spec files present
4. `output/` — list generated files (xlsx/docx/pptx) present

Output a status dashboard:

```
── EVENT PLANNING STATUS ─────────────────────────
  Event: <name or [not configured]>
  Date:  <date or [TBD]>

  Pipeline:
  [✅/⬜] 1. session-init     → event-context.md
  [✅/⬜] 2. venue-scout      → drafts/venues-*.md (<n> venues)
  [✅/⬜] 3. info-compiler    → drafts/compiled-*.md (optional)
  [✅/⬜] 4. budget-validator → drafts/budget-*.md (<status>)
  [✅/⬜] 5. event-planner    → drafts/planning-*.md
  [✅/⬜] 6. email-drafter    → <n> draft(s)
  [✅/⬜] 7. doc-generator    → <n> JSON spec(s)
  [✅/⬜] 8. py-dev           → output/ (<n> file(s))
  [✅/⬜] 9. gdrive-uploader  → Drive upload (optional)

  Next suggested step: <agent name and trigger>
──────────────────────────────────────────────────
```

## Rules

- Use ✅ when output file exists for that step; ⬜ when missing.
- For budget-validator: extract APPROVED/REJECTED from the file if present.
- Step 9 has no local artifact — mark ✅ only if the user confirmed an upload this session, else ⬜.
- Keep output concise — dashboard only, no prose.

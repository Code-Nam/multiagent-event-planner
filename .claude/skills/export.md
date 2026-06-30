---
name: export
description: Generate all official event documents (xlsx, docx, ppt) from current drafts via doc-generator.
---

Trigger document generation for all available draft data. Delegates to `doc-generator` once per document type.

## Steps

1. **Check available drafts** — list files in `drafts/` and `doc-content/`.
2. **Determine which docs to generate** based on args or default to all 3:
   - `xlsx` → budget recap + venue comparison + task tracking
   - `docx` → full event report
   - `ppt` → presentation slides
3. **Delegate to doc-generator** for each requested type, passing:
   - Document type
   - Paths to all relevant draft files found in step 1
   - Event name and date from `event-context.md`

## Args (optional)

Pass one or more of: `xlsx` `docx` `ppt`

Examples:
- `/export` → generates all 3
- `/export xlsx` → Excel only
- `/export docx ppt` → report + presentation

## After generation

Report:

```
── EXPORT COMPLETE ───────────────────────────────
  doc-content/xlsx_recap-<slug>.json   ✅
  doc-content/docx_report-<slug>.json  ✅
  doc-content/ppt_presentation-<slug>.json ✅

  Run generation scripts:
    python scripts/generate_xlsx.py doc-content/xlsx_recap-<slug>.json
    python scripts/generate_docx.py doc-content/docx_report-<slug>.json
    python scripts/generate_ppt.py  doc-content/ppt_presentation-<slug>.json
──────────────────────────────────────────────────
```

## Rules

- If a draft file is missing for a requested doc type: warn but continue with available data.
- JSON specs go to `doc-content/` — actual file generation requires Phase 2 Python scripts.
- Never generate docs if event-context.md is still template.

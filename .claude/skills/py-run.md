---
name: py-run
description: Run Phase 2 document generation scripts against JSON specs in doc-content/. Writes scripts if missing, then executes. Output goes to output/.
---

Generate actual xlsx/docx/pptx files from JSON specs produced by doc-generator.

## Args (optional)

`/py-run` or `/py-run all` → all 3 types  
`/py-run xlsx` → Excel only  
`/py-run docx ppt` → report + presentation

## Steps

1. **Check doc-content/** — if no JSON specs found, stop and tell user to run `/export` first.
2. **Resolve types** — no args / `all` = xlsx + docx + ppt. Skip any type whose spec is missing (warn user).
3. **For each type** (sequential — wait for receipt before next):
   - Delegate to `py-dev` with: task = "document generation", script type, full path to matching JSON spec.
4. **Report summary:**

```
── PY-RUN COMPLETE ───────────────────────────────
  output/<slug>.xlsx   ✅ / ⚠️ skipped (no spec)
  output/<slug>.docx   ✅ / ⚠️ skipped (no spec)
  output/<slug>.pptx   ✅ / ⚠️ skipped (no spec)
──────────────────────────────────────────────────
```

## Rules

- Sequential only — one script at a time.
- On missing spec: warn and skip that type, continue with others.
- Never modify JSON specs in doc-content/.
- If py-dev reports a pip import error: surface the `pip install` command to user.

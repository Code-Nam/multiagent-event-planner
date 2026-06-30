---
name: budget-override
description: Confirm and relay a budget override after a 🔴 REJECTED validation. Requires explicit user confirmation before proceeding.
---

Use only after budget-validator has returned 🔴 REJECTED status.

## Steps

1. Read `drafts/budget-*.md` — extract the rejection summary (total expenses, overspend amount, fixed budget).
2. Display to user:

```
── BUDGET OVERRIDE REQUEST ───────────────────────
  Fixed budget:    €<amount>
  Total expenses:  €<amount>
  Overspend:       €<amount> (<percent>% over)

  ⚠️  This will approve an over-budget plan.
  Type CONFIRMER to proceed, anything else to cancel.
──────────────────────────────────────────────────
```

3. Wait for user response.
   - If user types `CONFIRMER` (exact, case-insensitive): delegate to budget-validator with explicit message `"override budget"` + the expense file path. Receipt the result.
   - Anything else: cancel, no delegation, inform user budget remains rejected.

## Rules

- Never self-approve — always wait for explicit user confirmation.
- Never trigger without a prior 🔴 REJECTED file in drafts/.
- If no rejected budget file found: tell user to run budget-validator first.
- One override per invocation — do not persist override state across sessions.

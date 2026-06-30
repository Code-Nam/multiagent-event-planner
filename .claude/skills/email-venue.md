---
name: email-venue
description: Draft a venue inquiry email (venue_inquiry) for the recommended venue, auto-filled from compiled drafts. Shortcut for the most common email-drafter use case.
---

Draft a professional venue inquiry email without requiring manual context entry.

## Steps

1. Read `event-context.md` — extract event name, date, type, attendance, lead name.
2. Read `drafts/compiled-*.md` — extract the 1st choice venue: name, address, contact (email/phone), estimated price.
   - If no compiled file exists: read `drafts/venues-*.md` and use the first venue listed.
   - If no draft files at all: stop, tell user to run venue-scout first.
3. Check args for optional overrides:
   - `/email-venue <venue-name>` → use that specific venue instead of the recommendation
   - `/email-venue` → use recommended venue (default)
4. Delegate to `email-drafter` with:
   - Purpose: `venue_inquiry`
   - Recipient: venue name + contact extracted in step 2
   - Details: event type, date, expected attendance, budget range, any special requirements from event-context.md
   - Instruction: read event-context.md for full context

## Receipt passthrough

Forward email-drafter's receipt verbatim, then add:

```
  auto-filled from: <source draft file>
  venue targeted:   <venue name>
```

## Rules

- Never invent contact details — use only what is in the draft files.
- If contact email/phone is `[on request]` or missing: include `[To complete]` in the draft, do not block.
- Draft only — never send.

---
name: event-recap
description: Single-page synthesis of all planning decisions so far. Reads event-context and all drafts, outputs a human-readable briefing.
---

Produce a concise briefing document from all available planning data. Useful before stakeholder meetings or to share current state.

## Steps

1. Read `event-context.md`.
2. Scan `drafts/` — read all files present:
   - `venues-*.md` → venue search results
   - `compiled-*.md` → recommended venue
   - `budget-*.md` → budget status
   - `planning-*.md` → tasks, timeline, contacts
   - email drafts → outreach status
3. Synthesise into the format below. Skip sections where no data exists — do not write `[TBD]` blocks.

## Output format

```markdown
# Récapitulatif — <Event name>
<Date> · <Type> · <Attendance> personnes · Budget : €<amount>

## Événement
<2-3 sentences: what, where (area), when, who leads>

## Lieu retenu
**<Venue name>** — <address>
Prix estimé : €<amount> · Contact : <email or phone>
<1-line reason for selection if available>

## Budget
Statut : ✅ APPROUVÉ / 🔴 REJETÉ (dépassement : €<amount>)
| Poste | Montant | % budget |
|-------|---------|----------|
| ...   | ...     | ...      |

## Planning opérationnel
Prochaines tâches :
- <Task> — <Owner> — <Deadline>
- ...

Jour J (<date>) :
- <Time> <Action>
- ...

## Contacts clés
| Nom | Rôle | Contact |
|-----|------|---------|

## Emails en cours
- <purpose> → <recipient> — statut : draft
```

## Rules

- Output in French — this is a stakeholder-facing document.
- Only include sections with real data — omit empty sections entirely.
- No invented data — `[To complete]` only for fields explicitly marked as such in source files.
- Do not write to disk — output to conversation only (user copies if needed).

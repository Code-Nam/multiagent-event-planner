# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

/caveman

@event-context.md

## Session Setup

Each session = one AGEVP event project.

1. Read `event-context.md` — if blank/template → **run `session-init` immediately**.
2. If populated → ask: "Continue the current event or start a new one?"
3. No event work until `event-context.md` is filled.

## Dev Environment

This repo uses a token-optimization stack — all three tools are active per session:

- **RTK** (`~/.cargo/bin/rtk`) — CLI proxy, auto-routes Bash commands via `PreToolUse` hook. Use `rtk gain` to see savings.
- **context-mode** — MCP plugin, keeps large tool outputs out of conversation context. Use `/context-mode:ctx-doctor` to verify.
- **caveman** — active by default (full level). Use `/caveman lite|full|ultra` to adjust intensity.

## Git Commits

All commits must follow [Conventional Commits](https://www.conventionalcommits.org/):

```text
<type>[(scope)]: <description>

[optional body]

[optional footer]
```

**Allowed types:** `feat` `fix` `chore` `docs` `refactor` `test` `ci` `perf` `style` `build` `revert`

**Scope:** optional. When used, lowercase noun — `feat(auth):`, `fix(api):`.

**Breaking changes:** footer only — `BREAKING CHANGE: <description>`. Never use `!` suffix.

**Rules:**

- Description: imperative mood, lowercase, no period — `add user login` not `Added user login.`
- Subject line ≤ 72 chars
- Body: wrap at 72 chars, explain *why* not *what*
- One logical change per commit

## Agent Delegation

This session is the **supervisor**. Delegate to specialists — never do event work inline.

### Event Planning Agents

| Agent | Role | When to use |
|-------|------|-------------|
| `session-init` | Session init, writes event-context.md | Always first — blank context |
| `venue-scout` | Search Paris venues via web + scraping | "find venue", "chercher salle" |
| `info-compiler` | Comparison table + ranked recommendation | After venue-scout |
| `budget-validator` | Validate expenses vs fixed budget | "check budget", "on a X€", expense list |
| `event-planner` | Tasks, materials, timeline, contacts | "who does what", "plan the day", "assign roles" |
| `email-drafter` | Draft professional emails (no send) | "write to", "contacter", "email for" |
| `doc-generator` | JSON content specs for docs (xlsx/docx/ppt) | "recap file", "document", "Excel", "presentation" |

### Event planning flow (full path)

```
1. session-init     → event-context.md
2. venue-scout      → drafts/venues-*.md
3. info-compiler    → drafts/compiled-*.md
4. budget-validator → drafts/budget-*.md
5. event-planner    → drafts/planning-*.md
6. email-drafter    → drafts/<purpose>-*.md
7. doc-generator    → doc-content/*.json
```

Flow is a guide — user can jump to any step.

### Receipt format (all agents)

```
receipt:
- agent: <name>
- status: done | partial | blocked
- output: <file path or 1-line summary>
- next: <suggested agent>
```

### Hard rules

- Always pass explicitly into each delegation: file paths, context, prior decisions
- Subagents start with no shared memory — every delegation must be self-contained
- `email-drafter`: draft only, never send
- `budget-validator`: flag 🔴 if over budget — requires explicit `"override budget"` to proceed

# AGEVP Multi-Agent Event Planner

Claude Code workspace for planning events at [AGEVP](https://www.agevp.com/wordpress/fr/accueil/qui-sommes-nous/) — Association Générale des Étudiants Vietnamiens de Paris.

Each Claude Code session = one event project. A supervisor orchestrates 7 specialised agents that handle venue search, budget validation, operational planning, email drafting, and document generation.

---

## How it works

Open this repo in Claude Code. The session initialises automatically:

1. `event-context.md` is loaded into context via `@import` in `CLAUDE.md`
2. A `SessionStart` hook reminds the supervisor to check it
3. If blank → `session-init` agent runs and collects event details
4. If populated → supervisor asks: continue or new event?

From there, ask naturally. The supervisor routes to the right agent.

---

## Agents

| Agent | Role | Output |
|-------|------|--------|
| `session-init` | Collect event details, write `event-context.md` | `event-context.md` |
| `venue-scout` | Search Paris venues via web + scraping | `drafts/venues-*.md` |
| `info-compiler` | Comparison table + ranked recommendation | `drafts/compiled-*.md` |
| `budget-validator` | Validate expenses vs fixed budget | `drafts/budget-*.md` |
| `event-planner` | Tasks, materials, timeline, contacts | `drafts/planning-*.md` |
| `email-drafter` | Draft professional emails in French (no send) | `drafts/<purpose>-*.md` |
| `doc-generator` | JSON content specs for xlsx/docx/ppt | `doc-content/*.json` |

### Full planning flow

```
session-init → venue-scout → info-compiler → budget-validator
                                           → event-planner
                                           → email-drafter
                                           → doc-generator
```

Jump to any step — flow is a guide, not a requirement.

---

## File structure

```
.
├── .claude/
│   ├── agents/               # 7 event planning agent definitions
│   └── settings.json         # SessionStart hook + plugins config
├── drafts/                   # Generated per-session (gitignored)
├── doc-content/              # JSON doc specs per-session (gitignored)
├── event-context.md          # Current event context (populated by session-init)
└── CLAUDE.md                 # Supervisor instructions + routing table
```

`drafts/` and `doc-content/` accumulate outputs per session. `event-context.md` is overwritten each session.

---

## Phases

| Phase | Status | Scope |
|-------|--------|-------|
| **1 — Agents** | ✅ Done | 7 agents, session init, supervisor routing |
| **2 — Scripts** | Planned | Python mail sender (Gmail API), doc generator (openpyxl / python-docx), Google Drive MCP |
| **3 — Web app** | Planned | API + frontend |

---

## Dev tooling

This repo runs a token-optimisation stack to reduce Claude Code token consumption.

| Tool | What it does | Savings |
|------|-------------|---------|
| **RTK** | Filters CLI output before Claude sees it | 60–90% per command |
| **context-mode** | Keeps large tool results out of conversation | 40–70% per session |
| **caveman** | Compresses Claude prose responses | ~75% per response |

### RTK — Rust Token Killer

```bash
cargo install --git https://github.com/rtk-ai/rtk
```

Wire into `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "rtk hook claude" }]
      }
    ]
  }
}
```

```bash
rtk gain              # token savings analytics
rtk gain --history    # per-command savings
rtk discover          # scan history for missed optimizations
```

> **Name collision:** If `rtk gain` fails, you may have `reachingforthejack/rtk` (Rust Type Kit) installed. Check `which rtk`.

### context-mode

Inside Claude Code:

```
/plugin marketplace add mksglu/context-mode
/plugin install context-mode@context-mode
```

Restart or `/reload-plugins`. Verify with `/context-mode:ctx-doctor`.

### caveman

```bash
npx -y github:JuliusBrussee/caveman -- --all
```

Toggle: `/caveman` · Intensity: `/caveman lite|full|ultra` · Off: `stop caveman`

### Full settings.json

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "rtk hook claude" }]
      }
    ]
  },
  "enabledPlugins": {
    "context-mode@context-mode": true
  },
  "extraKnownMarketplaces": {
    "context-mode": { "source": { "source": "github", "repo": "mksglu/context-mode" } },
    "caveman": { "source": { "source": "github", "repo": "JuliusBrussee/caveman" } }
  }
}
```

Caveman hooks are written by its installer — no manual JSON edit needed.

### Verify stack

```bash
rtk --version
rtk gain
```

Inside Claude Code:

```
/context-mode:ctx-doctor
/caveman
```

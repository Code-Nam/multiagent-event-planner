# AGEVP Multi-Agent Event Planner

Claude Code workspace for planning events at [AGEVP](https://www.agevp.com/wordpress/fr/accueil/qui-sommes-nous/) — Association Générale des Étudiants Vietnamiens de Paris.

Each Claude Code session = one event project. A supervisor orchestrates 12 specialised agents that handle venue search, budget validation, operational planning, email drafting, document generation, Python script execution, and config auditing.

---

## How it works

Open this repo in Claude Code. The session initialises automatically:

1. `event-context.md` is loaded into context via `@import` in `CLAUDE.md`
2. A `SessionStart` hook reminds the supervisor to check it
3. If blank → `session-init` agent runs and collects event details
4. If populated → supervisor asks: continue or new event?

From there, ask naturally. The supervisor routes to the right agent.

### Slash commands

| Command | What it does |
|---------|-------------|
| `/new-event` | Reset `event-context.md` to blank template and launch `session-init` |
| `/plan-status` | Show current planning progress — ✅/⬜ per pipeline step |
| `/full-pipeline` | Run full pipeline sequentially: venue-scout → compile → validate → plan |
| `/venue-pipeline` | Run venue phase only: scout → compile → validate |
| `/email-venue` | Draft venue inquiry email auto-filled from compiled drafts |
| `/budget-override` | Confirm and relay budget override after 🔴 rejection |
| `/event-recap` | Single-page French briefing synthesised from all drafts |
| `/export` | Generate xlsx/docx/ppt JSON specs via doc-generator |
| `/py-run` | Run generation scripts against JSON specs in doc-content/ — writes output/ files |
| `/py-gmail` | Push latest email-drafter output to Gmail as an API draft (not sent) |
| `/claude-review` | Audit all Claude config files — prioritised improvement plan |
| `/sync-docs` | Sync README, CLAUDE.md, settings to current agents and skills |
| `/api-run` | Start FastAPI dev server at `http://localhost:8000` |
| `/webapp-run` | Start Vue 3 dev server at `http://localhost:5173` |

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
| `claude-reviewer` | Read-only config audit — prioritised improvement plan | conversation only |
| `doc-updater` | Sync README, CLAUDE.md, settings to current config | in-place edits |
| `py-dev` | Python coding specialist — writes/runs scripts for document generation and Gmail API draft creation | `output/` files, Gmail draft ID |
| `api-dev` | Build/maintain FastAPI routes, Pydantic models, services | `api/` files |
| `webapp-dev` | Build/maintain Vue 3 SPA — views, components, Pinia stores, composables | `webapp/` files |

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
│   ├── agents/               # 12 agent definitions
│   ├── skills/               # 13 slash commands
│   ├── hooks/                # SessionStart preview script
│   └── settings.json         # Hooks + plugin config
├── api/                      # FastAPI backend
│   ├── routes/               # event, drafts, generate, agents, status
│   ├── services/             # file_store, script_runner, agent_runner
│   ├── tests/                # 55 pytest tests
│   └── requirements.txt
├── webapp/                   # Vue 3 SPA
│   ├── src/
│   │   ├── composables/      # use-api, use-sse
│   │   ├── stores/           # event, drafts, pipeline, output
│   │   ├── views/
│   │   └── components/
│   └── package.json
├── scripts/                  # Python doc generators (Phase 2)
├── drafts/                   # Per-session outputs (gitignored)
├── doc-content/              # JSON doc specs (gitignored)
├── output/                   # Generated xlsx/docx/pptx (gitignored)
├── event-context.md          # Current event (populated by session-init)
└── CLAUDE.md                 # Supervisor instructions + routing table
```

`drafts/`, `doc-content/`, and `output/` are gitignored — populated per session.

### Running tests

```bash
# API (requires venv)
cd api && python -m venv venv && venv/bin/pip install -r requirements.txt
venv/bin/pytest tests/ -q

# Webapp
cd webapp && npm install && npm test -- --run
```

---

## Phases

| Phase | Status | Scope |
|-------|--------|-------|
| **1 — Agents** | ✅ Done | 12 agents, 13 skills, session init, supervisor routing |
| **2 — Scripts** | In progress | Python doc generator (openpyxl / python-docx / python-pptx), Gmail API draft creation |
| **3 — Web app** | In progress | FastAPI (`api/`) + Vue 3 SPA (`webapp/`) — agents and tests in place |

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

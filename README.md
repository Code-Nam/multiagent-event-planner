# AGEVP Multi-Agent Event Planner

Claude Code workspace for planning events at [AGEVP](https://www.agevp.com/wordpress/fr/accueil/qui-sommes-nous/) — Association Générale des Étudiants Vietnamiens de Paris.

Each Claude Code session = one event project. A supervisor orchestrates 13 specialised agents covering venue search, budget validation, operational planning, email drafting, document generation, and Google Drive upload.

The repo also ships a **Claude Code Token Dashboard** — a local FastAPI + Vue 3 app that reads `~/.claude/` to show token usage per session. It lives in `api/` and `webapp/` and is meant to run alongside active Claude Code sessions.

---

## Quick start

### 1. Environment

```bash
cp .env.example .env
```

Edit `.env` — the key variables:

```env
CLAUDE_DIR=/home/YOUR_USER/.claude    # path to your ~/.claude directory
API_PORT=8001                          # token dashboard API port (default 8001)
WEBAPP_PORT=5174                       # token dashboard webapp port (default 5174)
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
VITE_API_BASE=http://localhost:8001
VITE_PROJECT_SLUG=home-YOUR_USER-Github-YOUR_REPO
```

> `ANTHROPIC_API_KEY` is **not** needed by the token dashboard — it is only required if you run Claude Code agents directly (and Claude Code itself handles it). Optional Gmail API vars (`GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`) are only needed for `/py-gmail`.

### 2. Event context

```bash
cp event-context.example.md event-context.md
```

Fill in `event-context.md` with your event details. `event-context.md` is gitignored — your local data is never committed.

### 3. Run with Docker

```bash
docker compose up --build
```

The API container mounts `~/.claude` read-only (`~/.claude:/root/.claude:ro`) so the token dashboard can read your session data without any write access.

| Service | URL |
|---------|-----|
| Token dashboard webapp | http://localhost:5173 |
| Token dashboard API | http://localhost:8000 |

### 4. Local dev (no Docker)

```bash
# API
cd api && pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

# Webapp
cd webapp && npm install
npm run dev
```

Or use the `dev.sh` script at the project root, which starts both services.

---

## How it works

**Claude Code** — open this repo in Claude Code. The session initialises automatically:

1. `event-context.md` is loaded into context via `@import` in `CLAUDE.md`
2. A `SessionStart` hook reminds the supervisor to check it
3. If blank → `session-init` agent runs and collects event details
4. If populated → supervisor asks: continue or new event?

Ask naturally — the supervisor routes to the right specialist agent.

**Token dashboard** (`http://localhost:5173`) — Vue 3 SPA. Shows all Claude Code sessions with per-agent token breakdowns, a live indicator for running sessions, and a session detail view.

---

## Token Dashboard

### API reference

FastAPI app at `api/main.py` ("Claude Code Token Dashboard"). Reads `~/.claude/` JSONL files via `api/services/token_reader.py`.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Returns `{"ok": true}` if `~/.claude` dir is accessible |
| GET | `/api/jobs` | List sessions. Query params: `limit` (1–200, default 50), `project` (filter by project) |
| GET | `/api/jobs/{job_id}` | Full detail for one session including token breakdown |
| POST | `/api/jobs/live` | SSE stream of live token updates for a running session. Body: `{"job_id": "..."}` |
| WS | `/api/jobs/{job_id}/ws` | WebSocket equivalent of the live stream |

### Webapp

Stack: Vue 3 + Vite + TypeScript + Tailwind + Pinia + Vue Router 4

| Route | What it shows |
|-------|--------------|
| `/sessions` | All Claude Code sessions with token counts |
| `/sessions/:sessionId` | Session detail — agent breakdown, token bar, live indicator |

Key components: `agent-breakdown-table`, `session-summary-card`, `token-bar`, `live-indicator`, `state-badge`

---

## Slash commands

| Command | What it does |
|---------|-------------|
| `/plan-status` | Show current planning progress — ✅/⬜ per pipeline step |
| `/full-pipeline` | Run full pipeline: venue-scout → compile → validate → plan |
| `/venue-pipeline` | Venue phase only: scout → compile → validate |
| `/email-venue` | Draft venue inquiry email auto-filled from compiled drafts |
| `/budget-override` | Confirm and relay budget override after 🔴 rejection |
| `/event-recap` | Single-page synthesis of all planning decisions so far |
| `/export` | Generate xlsx/docx/ppt JSON specs via doc-generator |
| `/py-run` | Run generation scripts → writes `output/` files |
| `/py-gmail` | Push latest email draft to Gmail as API draft (not sent) |
| `/gdrive-upload` | Upload all `output/` files to Google Drive — returns folder + per-file links |
| `/new-event` | Reset `event-context.md` and run session-init for a new event (confirms first) |
| `/claude-review` | Audit all Claude config files — prioritised improvement plan |
| `/sync-docs` | Sync README, CLAUDE.md, settings to current agents and skills |
| `/api-run` | Start FastAPI dev server at `http://localhost:8000` |
| `/webapp-run` | Start Vue 3 dev server at `http://localhost:5173` |

---

## Agents

| Agent | Role | Output |
|-------|------|--------|
| `session-init` | Session initializer — collects event details, writes `event-context.md` | `event-context.md` |
| `venue-scout` | Search Paris venues via web search and scraping | `drafts/venues-*.md` |
| `info-compiler` | Comparison table + ranked recommendation from raw venue data | `drafts/compiled-*.md` |
| `budget-validator` | Validate proposed expenses against fixed budget | `drafts/budget-*.md` |
| `event-planner` | Tasks, materials checklist, timeline, key contacts | `drafts/planning-*.md` |
| `email-drafter` | Draft professional emails in French — no send, draft only | `drafts/<purpose>-*.md` |
| `doc-generator` | JSON content specs for xlsx/docx/ppt output files | `doc-content/*.json` |
| `py-dev` | Write/run Python scripts for doc generation and Gmail API drafts | `output/`, Gmail draft ID |
| `gdrive-uploader` | Upload `output/` files to Google Drive under an event-named folder | Drive folder + per-file links |
| `claude-reviewer` | Read-only audit of all Claude config files | conversation |
| `doc-updater` | Sync README, CLAUDE.md, settings to current agent/skill set | in-place edits |
| `api-dev` | Build/maintain FastAPI routes, Pydantic models, services | `api/` |
| `webapp-dev` | Build/maintain Vue 3 SPA — views, components, Pinia stores, composables | `webapp/` |

### Planning flow

```
1. session-init              → event-context.md
2. venue-scout               → drafts/venues-*.md
3. info-compiler (optional)  → drafts/compiled-*.md
4. budget-validator          → drafts/budget-*.md
5. event-planner             → drafts/planning-*.md
6. email-drafter             → drafts/<purpose>-*.md
7. doc-generator             → doc-content/*.json
8. py-dev (Phase 2)          → output/*.xlsx / *.docx / *.pptx  OR  Gmail draft ID
9. gdrive-uploader (optional) → Google Drive folder + per-file links
```

Jump to any step — flow is a guide, not a requirement.

---

## File structure

```
.
├── .claude/
│   ├── agents/               # 13 agent definitions
│   ├── skills/               # 15 slash commands
│   ├── hooks/                # SessionStart preview + PreToolUse RTK proxy
│   └── settings.json
├── api/                      # FastAPI — Claude Code Token Dashboard backend
│   ├── routes/
│   │   ├── health.py         # GET /api/health
│   │   └── jobs.py           # GET/POST /api/jobs, WS /api/jobs/{id}/ws
│   ├── services/
│   │   └── token_reader.py   # Reads ~/.claude/ JSONL files
│   ├── tests/
│   └── requirements.txt
├── webapp/                   # Vue 3 SPA — token dashboard UI
│   ├── src/
│   │   ├── composables/      # use-api, use-sse, use-ws
│   │   ├── stores/           # sessions, session-detail
│   │   ├── views/            # sessions-view, session-detail-view
│   │   └── components/       # agent-breakdown-table, token-bar, live-indicator, ...
│   └── package.json
├── scripts/                  # Python doc generators (xlsx, docx, ppt)
├── drafts/                   # Per-session agent outputs (gitignored)
├── doc-content/              # JSON doc specs (gitignored)
├── output/                   # Generated xlsx/docx/pptx (gitignored)
├── event-context.md          # Current event config — local only (skip-worktree)
├── event-context.example.md  # Template showing expected format
├── docker-compose.yml        # api + webapp services
├── dev.sh                    # Local dev launcher
└── CLAUDE.md                 # Supervisor instructions + routing table
```

---

## Running tests

```bash
# API
cd api && python -m venv venv && venv/bin/pip install -r requirements.txt
venv/bin/pytest tests/ -q

# Webapp
cd webapp && npm install && npm test -- --run
```

---

## Dev tooling

Token-optimisation stack active by default in Claude Code sessions.

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

> **Name collision:** `rtk gain` failing → you may have `reachingforthejack/rtk` (Rust Type Kit). Check `which rtk`.

### context-mode

Inside Claude Code:

```
/plugin marketplace add mksglu/context-mode
/plugin install context-mode@context-mode
```

Verify: `/context-mode:ctx-doctor`

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

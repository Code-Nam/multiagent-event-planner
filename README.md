# Token-Saver Stack: RTK + context-mode + caveman

Three tools that compound. Each attacks a different layer of LLM token waste.

| Tool | What it kills | Savings |
|------|--------------|---------|
| **RTK** | Raw CLI output bloat (git, gh, docker, etc.) | 60–90% per command |
| **context-mode** | Oversized tool results entering conversation | 40–70% per session |
| **caveman** | Verbose Claude prose responses | ~75% per response |

---

## Prerequisites

- [Claude Code](https://claude.ai/code) v1.0.33+
- Rust toolchain (`curl https://sh.rustup.rs | sh`)
- Node.js 18+

---

## 1. RTK — Rust Token Killer

CLI proxy. Intercepts Bash commands, filters output to essential lines before Claude sees them.

**Install:**

```bash
cargo install --git https://github.com/rtk-ai/rtk
```

Verify:

```bash
rtk --version   # rtk X.Y.Z
rtk gain        # should show savings stats (not "command not found")
```

> **Name collision:** If `rtk gain` fails, you likely have `reachingforthejack/rtk` (Rust Type Kit) installed instead. Check `which rtk` and remove the wrong one.

**Wire into Claude Code** — add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "rtk hook claude"
          }
        ]
      }
    ]
  }
}
```

Now every `git status`, `gh pr view`, `docker ps`, etc. runs through RTK automatically.

**Usage:**

```bash
rtk gain              # token savings analytics
rtk gain --history    # command history with per-call savings
rtk discover          # scan Claude Code history for missed optimization opportunities
rtk proxy <cmd>       # run raw command without RTK filtering (debug)
```

---

## 2. context-mode

Claude Code plugin. Keeps large tool outputs out of conversation context — they go into a sandboxed FTS5 knowledge base instead. You query what you need; raw bytes never enter Claude's memory.

**Install** (inside Claude Code):

```
/plugin marketplace add mksglu/context-mode
/plugin install context-mode@context-mode
```

Restart Claude Code or run `/reload-plugins`.

**Verify:**

```
/context-mode:ctx-doctor
```

All checks should show `[x]`.

**Key slash commands:**

```
/context-mode:ctx-stats    # token savings breakdown for current session
/context-mode:ctx-doctor   # diagnostics — runtimes, hooks, FTS5, versions
/context-mode:ctx-upgrade  # pull latest, rebuild
/context-mode:ctx-purge    # wipe knowledge base (destructive)
/context-mode:ctx-search   # search indexed content
```

**Status line (optional)** — one-time edit to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash \"/path/to/context-mode/caveman-statusline.sh\""
  }
}
```

---

## 3. caveman

Claude Code plugin + hooks. Makes Claude respond like a compressed caveman — same technical accuracy, ~75% fewer tokens. Supports intensity levels.

**Install:**

```bash
# macOS / Linux / WSL
curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash
```

Or without `curl | bash`:

```bash
npx -y github:JuliusBrussee/caveman -- --all
```

Or from a clone:

```bash
git clone https://github.com/JuliusBrussee/caveman.git
cd caveman
node bin/install.js --dry-run --all   # preview first
node bin/install.js --all
```

**Verify** (inside Claude Code):

```
/caveman
```

**Intensity levels:**

```
/caveman lite    # drop filler only, keep full sentences
/caveman full    # fragments OK, drop articles (default)
/caveman ultra   # maximum compression
```

**Off:**

```
stop caveman
```

**Uninstall:**

```bash
npx -y github:JuliusBrussee/caveman -- --uninstall
```

---

## Full settings.json reference

Minimal working config combining all three tools:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "rtk hook claude"
          }
        ]
      }
    ]
  },
  "enabledPlugins": {
    "context-mode@context-mode": true
  },
  "extraKnownMarketplaces": {
    "context-mode": {
      "source": {
        "source": "github",
        "repo": "mksglu/context-mode"
      }
    },
    "caveman": {
      "source": {
        "source": "github",
        "repo": "JuliusBrussee/caveman"
      }
    }
  }
}
```

Caveman hooks are written by its installer — no manual JSON edit needed.

---

## Stack verification

```bash
rtk --version                    # RTK binary present
rtk gain                         # RTK hook active (shows stats)
```

Inside Claude Code:

```
/context-mode:ctx-doctor         # context-mode healthy
/caveman                         # caveman mode on
```

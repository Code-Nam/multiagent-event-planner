# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

/caveman

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

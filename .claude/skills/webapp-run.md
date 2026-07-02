---
name: webapp-run
description: Start the AGEVP Vue 3 webapp dev server (Vite) at port 5173. Delegates to webapp-dev if webapp/ does not exist or is missing key files. Prints the dev URL on success.
triggers:
  - /webapp-run
---

# /webapp-run

## What it does

Starts the Vite dev server so the AGEVP UI is accessible at `http://localhost:5173`.

## Steps

1. Check `webapp/` directory exists. If missing → delegate to `webapp-dev` to scaffold it.
2. Check `webapp/package.json` exists. If missing → delegate to `webapp-dev`.
3. Install dependencies if needed: `cd webapp && npm install`
4. Ensure `webapp/.env` (or `webapp/.env.local`) has `VITE_API_BASE` set. Warn if missing.
5. Start dev server: `cd webapp && npm run dev`
6. Print: `Webapp running at http://localhost:5173`

## Pre-requisite

API must be running at `VITE_API_BASE` (default `http://localhost:8000`). Run `/api-run` first.

## Delegate to `webapp-dev` when

- `webapp/` does not exist
- A view, component, or store is missing
- TypeScript errors need fixing

## Rules

- Port 5173 already in use → report the conflicting process, do not kill it without asking.
- `npm install` failure → report stderr, status blocked — never continue with missing deps.
- `VITE_API_BASE` missing → warn and continue; the app will surface API errors itself.

## receipt format

```
receipt:
- agent: webapp-run (skill)
- status: done | blocked
- output: http://localhost:5173
- next: open browser at http://localhost:5173
```

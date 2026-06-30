---
name: frontend-run
description: Start the AGEVP Vue 3 frontend dev server (Vite) at port 5173. Delegates to frontend-dev if frontend/ does not exist or is missing key files. Prints the dev URL on success.
triggers:
  - /frontend-run
---

# /frontend-run

## What it does

Starts the Vite dev server so the AGEVP UI is accessible at `http://localhost:5173`.

## Steps

1. Check `frontend/` directory exists. If missing → delegate to `frontend-dev` to scaffold it.
2. Check `frontend/package.json` exists. If missing → delegate to `frontend-dev`.
3. Install dependencies if needed: `cd frontend && npm install`
4. Ensure `frontend/.env` (or `frontend/.env.local`) has `VITE_API_BASE` set. Warn if missing.
5. Start dev server: `cd frontend && npm run dev`
6. Print: `Frontend running at http://localhost:5173`

## Pre-requisite

API must be running at `VITE_API_BASE` (default `http://localhost:8000`). Run `/api-run` first.

## Delegate to `frontend-dev` when

- `frontend/` does not exist
- A view, component, or store is missing
- TypeScript errors need fixing

## receipt format

```
receipt:
- agent: frontend-run (skill)
- status: done | blocked
- output: http://localhost:5173
- next: open browser at http://localhost:5173
```

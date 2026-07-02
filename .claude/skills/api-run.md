---
name: api-run
description: Start the AGEVP FastAPI dev server (uvicorn) at port 8000. Delegates to api-dev if api/ directory is missing or incomplete. Prints the base URL on success.
triggers:
  - /api-run
---

# /api-run

## What it does

Starts the FastAPI server so the frontend can reach `http://localhost:8000/api`.

## Steps

1. Check `api/main.py` exists. If missing → delegate to `api-dev` to build it first.
2. Check `api/requirements.txt` exists. If missing → delegate to `api-dev`.
3. Verify dependencies installed: `pip install -r api/requirements.txt` (skip if already installed).
4. Start server: `uvicorn api.main:app --reload --port 8000`
5. Print: `API running at http://localhost:8000`

## Delegate to `api-dev` when

- `api/main.py` does not exist
- A route or endpoint is missing
- A Pydantic model needs updating

## Rules

- Port 8000 already in use → report the conflicting process, do not kill it without asking.
- `pip install` failure → report stderr, status blocked — never continue with missing deps.
- Missing `.env` values (e.g. `CLAUDE_DIR`) → warn but start anyway; the API reports its own config errors.

## receipt format

```
receipt:
- agent: api-run (skill)
- status: done | blocked
- output: http://localhost:8000
- next: /webapp-run to start the Vue dev server
```

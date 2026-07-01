import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncGenerator

from api.config import JOBS_DIR, PROJECTS_DIR
from api.models import AgentMeta, Job, JobDetail, JobList, LiveSnapshot, TokenUsage

TERMINAL_STATES: frozenset[str] = frozenset({"done", "error", "stopped"})


def _extract_model(respawn_flags: list) -> str | None:
    try:
        idx = respawn_flags.index("--model")
        return respawn_flags[idx + 1]
    except (ValueError, IndexError):
        return None


def _safe_jsonl_path(raw: str) -> Path | None:
    """Return the resolved path only if it stays inside CLAUDE_DIR."""
    import api.config as _cfg
    resolved = Path(raw).resolve()
    try:
        resolved.relative_to(_cfg.CLAUDE_DIR.resolve())
        return resolved
    except ValueError:
        return None


def _parse_jsonl_usage(jsonl_path: Path) -> TokenUsage | None:
    if not jsonl_path.exists():
        return None
    counts = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
    }
    calls = 0
    try:
        with jsonl_path.open() as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("type") != "assistant":
                    continue
                usage = entry.get("message", {}).get("usage")
                if not isinstance(usage, dict):
                    continue
                calls += 1
                for k in counts:
                    counts[k] += usage.get(k, 0)
    except OSError:
        return None
    if calls == 0:
        return None
    return TokenUsage(
        **counts,
        total_tokens=counts["input_tokens"]
        + counts["output_tokens"]
        + counts["cache_creation_input_tokens"]
        + counts["cache_read_input_tokens"],
        api_call_count=calls,
    )


def _load_agent_metas(jsonl_path: Path) -> list[AgentMeta]:
    sub_dir = jsonl_path.parent / jsonl_path.stem / "subagents"
    if not sub_dir.is_dir():
        return []
    metas: list[AgentMeta] = []
    for f in sub_dir.glob("*.meta.json"):
        try:
            raw = json.loads(f.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        agent_id = f.name.removesuffix(".meta.json")
        agent_jsonl = sub_dir / f"{agent_id}.jsonl"
        usage, model = _parse_chat_jsonl(agent_jsonl) if agent_jsonl.exists() else (None, None)
        metas.append(
            AgentMeta(
                agent_type=raw.get("agentType", "unknown"),
                description=raw.get("description", ""),
                spawn_depth=raw.get("spawnDepth", 1),
                usage=usage,
                model=model,
            )
        )
    return metas


def _state_to_job(job_id: str, state: dict) -> Job:
    return Job(
        id=job_id,
        name=state.get("name") or state.get("detail") or "",
        template=state.get("template", "unknown"),
        state=state.get("state", "unknown"),
        tokens=state.get("tokens", 0),
        model=_extract_model(state.get("respawnFlags") or []),
        cwd=state.get("cwd", ""),
        project=Path(state.get("cwd", "")).as_posix().lstrip("/").replace("/", "-"),
        created_at=state.get("createdAt", ""),
        updated_at=state.get("updatedAt", ""),
    )


def _mtime_iso(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def _session_name(jsonl_path: Path) -> str:
    ai_title = ""
    first_user_text = ""
    try:
        with jsonl_path.open() as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                t = entry.get("type")
                if t == "ai-title":
                    title = entry.get("aiTitle", "")
                    if title:
                        return title
                if t == "human" and not first_user_text:
                    content = entry.get("message", {}).get("content", "")
                    if isinstance(content, str):
                        first_user_text = content[:60]
                    elif isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                text = block.get("text", "").strip()
                                if text:
                                    first_user_text = text[:60]
                                    break
    except OSError:
        pass
    return ai_title or first_user_text


def _parse_chat_jsonl(jsonl_path: Path) -> tuple[TokenUsage | None, str | None]:
    """Parse a chat session JSONL. Returns (usage, model)."""
    counts = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
    }
    calls = 0
    model: str | None = None
    try:
        with jsonl_path.open() as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("type") != "assistant":
                    continue
                msg = entry.get("message", {})
                usage = msg.get("usage")
                if not isinstance(usage, dict):
                    continue
                if model is None:
                    model = msg.get("model")
                calls += 1
                for k in counts:
                    counts[k] += usage.get(k, 0)
    except OSError:
        return None, None
    if calls == 0:
        return None, None
    return (
        TokenUsage(
            **counts,
            total_tokens=counts["input_tokens"]
            + counts["output_tokens"]
            + counts["cache_creation_input_tokens"]
            + counts["cache_read_input_tokens"],
            api_call_count=calls,
        ),
        model,
    )


def list_project_sessions(
    limit: int = 200, project_filter: str | None = None
) -> list[Job]:
    """Walk PROJECTS_DIR and return one Job per chat session JSONL file."""
    if not PROJECTS_DIR.is_dir():
        return []
    sessions: list[Job] = []
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        project_name = project_dir.name.removeprefix("-")
        if project_filter and project_name != project_filter:
            continue
        for jsonl_file in project_dir.glob("*.jsonl"):
            if not _safe_jsonl_path(str(jsonl_file)):
                continue
            session_id = jsonl_file.stem
            usage, model = _parse_chat_jsonl(jsonl_file)
            if usage is None or usage.total_tokens == 0:
                continue
            name = _session_name(jsonl_file)
            try:
                ts = _mtime_iso(jsonl_file)
                age_s = (datetime.now(tz=timezone.utc) - datetime.fromisoformat(ts)).total_seconds()
                state = "working" if age_s < 60 else "done"
            except OSError:
                ts = ""
                state = "done"
            sessions.append(
                Job(
                    id=session_id,
                    name=name,
                    template="chat",
                    state=state,
                    tokens=usage.total_tokens,
                    model=model,
                    cwd="",
                    project=project_name,
                    created_at=ts,
                    updated_at=ts,
                    source="chat",
                    usage=usage,
                )
            )
    sessions.sort(key=lambda j: j.created_at, reverse=True)
    return sessions[:limit]


def list_jobs(limit: int = 50, project: str | None = None) -> JobList:
    jobs: list[Job] = []
    if JOBS_DIR.is_dir():
        for entry in JOBS_DIR.iterdir():
            if not entry.is_dir():
                continue
            state_file = entry / "state.json"
            if not state_file.exists():
                continue
            try:
                state = json.loads(state_file.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            job = _state_to_job(entry.name, state)
            if project and job.project != project:
                continue
            raw_link = state.get("linkScanPath")
            jsonl_path = _safe_jsonl_path(raw_link) if raw_link else None
            if jsonl_path:
                usage = _parse_jsonl_usage(jsonl_path)
                if usage:
                    updates: dict = {"usage": usage}
                    if not state.get("tokens"):
                        updates["tokens"] = usage.total_tokens
                    job = job.model_copy(update=updates)
            jobs.append(job)

    chat_sessions = list_project_sessions(project_filter=project)
    combined = jobs + chat_sessions
    combined.sort(key=lambda j: j.created_at, reverse=True)
    total = len(combined)
    return JobList(jobs=combined[:limit], total=total)


def _find_chat_jsonl(session_id: str) -> Path | None:
    """Search all project directories for a JSONL file matching session_id."""
    if not PROJECTS_DIR.is_dir():
        return None
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        candidate = project_dir / f"{session_id}.jsonl"
        if candidate.exists() and _safe_jsonl_path(str(candidate)):
            return candidate
    return None


def get_job_detail(job_id: str) -> JobDetail | None:
    state_file = JOBS_DIR / job_id / "state.json"
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text())
        except (json.JSONDecodeError, OSError):
            return None
        job = _state_to_job(job_id, state)
        raw_link = state.get("linkScanPath")
        jsonl_path = _safe_jsonl_path(raw_link) if raw_link else None
        usage = _parse_jsonl_usage(jsonl_path) if jsonl_path else None
        agents = _load_agent_metas(jsonl_path) if jsonl_path else []
        job_dict = job.model_dump()
        if usage:
            job_dict["tokens"] = usage.total_tokens
        job_dict.pop("usage", None)
        return JobDetail(**job_dict, usage=usage, agents=agents)

    # Fall back: look for a chat session JSONL with this UUID.
    jsonl_path = _find_chat_jsonl(job_id)
    if jsonl_path is None:
        return None
    usage, model = _parse_chat_jsonl(jsonl_path)
    if usage is None:
        return None
    name = _session_name(jsonl_path)
    project_name = jsonl_path.parent.name.removeprefix("-")
    try:
        ts = _mtime_iso(jsonl_path)
        age_s = (datetime.now(tz=timezone.utc) - datetime.fromisoformat(ts)).total_seconds()
        state = "working" if age_s < 60 else "done"
    except OSError:
        ts = ""
        state = "done"
    job = Job(
        id=job_id,
        name=name,
        template="chat",
        state=state,
        tokens=usage.total_tokens,
        model=model,
        cwd="",
        project=project_name,
        created_at=ts,
        updated_at=ts,
        source="chat",
    )
    job_dict = job.model_dump()
    job_dict.pop("usage", None)
    return JobDetail(**job_dict, usage=usage, agents=_load_agent_metas(jsonl_path))


async def ws_live_job(job_id: str, ws: "WebSocket") -> None:
    from fastapi import WebSocketDisconnect

    state_file = JOBS_DIR / job_id / "state.json"
    last_updated = ""
    last_jsonl_size = -1
    while True:
        try:
            state = json.loads(state_file.read_text())
        except (json.JSONDecodeError, OSError):
            await ws.send_text('{"error":"state unreadable"}')
            return
        updated = state.get("updatedAt", "")
        is_terminal = state.get("state") in TERMINAL_STATES
        raw_link = state.get("linkScanPath")
        jsonl_path = _safe_jsonl_path(raw_link) if raw_link else None
        jsonl_size = jsonl_path.stat().st_size if jsonl_path and jsonl_path.exists() else -1
        # Fire on state change, JSONL growth (new tokens), or terminal transition.
        if updated != last_updated or jsonl_size != last_jsonl_size or is_terminal:
            last_updated = updated
            last_jsonl_size = jsonl_size
            usage = _parse_jsonl_usage(jsonl_path) if jsonl_path else None
            snap = LiveSnapshot(
                job_id=job_id,
                state=state.get("state", ""),
                tokens=usage.total_tokens if usage else state.get("tokens", 0),
                updated_at=updated,
                usage=usage,
            )
            await ws.send_text(snap.model_dump_json())
        if is_terminal:
            return
        await asyncio.sleep(2)


async def stream_live_job(job_id: str) -> AsyncGenerator[str, None]:
    state_file = JOBS_DIR / job_id / "state.json"
    last_updated = ""
    last_jsonl_size = -1
    while True:
        try:
            state = json.loads(state_file.read_text())
        except (json.JSONDecodeError, OSError):
            yield f"event: error\ndata: {json.dumps({'message': 'state unreadable'})}\n\n"
            return
        updated = state.get("updatedAt", "")
        is_terminal = state.get("state") in TERMINAL_STATES
        raw_link = state.get("linkScanPath")
        jsonl_path = _safe_jsonl_path(raw_link) if raw_link else None
        jsonl_size = jsonl_path.stat().st_size if jsonl_path and jsonl_path.exists() else -1
        if updated != last_updated or jsonl_size != last_jsonl_size or is_terminal:
            last_updated = updated
            last_jsonl_size = jsonl_size
            usage = _parse_jsonl_usage(jsonl_path) if jsonl_path else None
            snap = LiveSnapshot(
                job_id=job_id,
                state=state.get("state", ""),
                tokens=usage.total_tokens if usage else state.get("tokens", 0),
                updated_at=updated,
                usage=usage,
            )
            yield f"event: snapshot\ndata: {snap.model_dump_json()}\n\n"
        if is_terminal:
            yield "event: done\ndata: {}\n\n"
            return
        await asyncio.sleep(2)

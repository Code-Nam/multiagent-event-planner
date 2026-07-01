import json
import pytest
from fastapi.testclient import TestClient

import api.config as cfg
import api.services.token_reader as tr


SAMPLE_STATE = {
    "state": "done",
    "detail": "test session",
    "tokens": 1234,
    "name": "test run",
    "template": "claude",
    "respawnFlags": ["--agent", "claude", "--permission-mode", "auto"],
    "sessionId": "aaaa-0000",
    "resumeSessionId": "aaaa-0000",
    "cwd": "/home/user/myproject",
    "createdAt": "2026-06-30T08:00:00.000Z",
    "updatedAt": "2026-06-30T09:00:00.000Z",
}

SAMPLE_STATE_BG = {
    **SAMPLE_STATE,
    "template": "bg",
    "respawnFlags": ["--permission-mode", "default", "--model", "claude-sonnet-4-6"],
    "name": "bg agent",
}

SAMPLE_JSONL = "\n".join([
    json.dumps({"type": "human", "message": {"role": "user", "content": "hello"}}),
    json.dumps({
        "type": "assistant",
        "message": {
            "role": "assistant",
            "model": "claude-sonnet-4-6",
            "content": [],
            "usage": {
                "input_tokens": 100,
                "output_tokens": 50,
                "cache_creation_input_tokens": 200,
                "cache_read_input_tokens": 300,
            },
        },
    }),
    json.dumps({
        "type": "assistant",
        "message": {
            "role": "assistant",
            "model": "claude-sonnet-4-6",
            "content": [],
            "usage": {
                "input_tokens": 10,
                "output_tokens": 5,
                "cache_creation_input_tokens": 20,
                "cache_read_input_tokens": 30,
            },
        },
    }),
])

SAMPLE_META = json.dumps({
    "agentType": "venue-scout",
    "description": "find venues",
    "spawnDepth": 1,
    "toolUseId": "toolu_abc123",
})


@pytest.fixture()
def tmp_claude(tmp_path, monkeypatch):
    jobs_dir = tmp_path / "jobs"
    projects_dir = tmp_path / "projects"
    jobs_dir.mkdir()
    projects_dir.mkdir()

    monkeypatch.setattr(cfg, "CLAUDE_DIR", tmp_path)
    monkeypatch.setattr(cfg, "JOBS_DIR", jobs_dir)
    monkeypatch.setattr(cfg, "PROJECTS_DIR", projects_dir)
    monkeypatch.setattr(tr, "JOBS_DIR", jobs_dir)
    monkeypatch.setattr(tr, "PROJECTS_DIR", projects_dir)

    return {"jobs": jobs_dir, "projects": projects_dir}


@pytest.fixture()
def client(tmp_claude):
    from api.main import app
    return TestClient(app)


def make_job(jobs_dir, job_id: str, state: dict, jsonl_content: str | None = None,
             metas: list[str] | None = None, projects_dir=None):
    job_dir = jobs_dir / job_id
    job_dir.mkdir()

    final_state = dict(state)
    if jsonl_content is not None and projects_dir is not None:
        jsonl_path = projects_dir / f"{job_id}.jsonl"
        jsonl_path.write_text(jsonl_content)
        final_state["linkScanPath"] = str(jsonl_path)

        if metas:
            sub_dir = projects_dir / job_id / "subagents"
            sub_dir.mkdir(parents=True)
            for i, meta in enumerate(metas):
                (sub_dir / f"agent-{i:016x}.meta.json").write_text(meta)

    (job_dir / "state.json").write_text(json.dumps(final_state))
    return job_id

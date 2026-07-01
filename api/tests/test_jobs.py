import json
from pathlib import Path

from api.tests.conftest import SAMPLE_JSONL, SAMPLE_META, SAMPLE_STATE, SAMPLE_STATE_BG, make_job

CHAT_JSONL = "\n".join([
    json.dumps({"type": "human", "message": {"content": "Help me plan an event"}}),
    json.dumps({
        "type": "assistant",
        "message": {
            "model": "claude-sonnet-4-6",
            "usage": {
                "input_tokens": 40,
                "output_tokens": 15,
                "cache_creation_input_tokens": 80,
                "cache_read_input_tokens": 160,
            },
        },
    }),
])


def _make_chat_session(projects_dir: Path, project: str, session_id: str, content: str):
    import os
    proj_dir = projects_dir / project
    proj_dir.mkdir(exist_ok=True)
    p = proj_dir / f"{session_id}.jsonl"
    p.write_text(content)
    os.utime(p, (1_000_000, 1_000_000))  # far past → state == "done"


def test_get_jobs_empty(client):
    resp = client.get("/api/jobs")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["jobs"] == []


def test_get_jobs_lists_all(client, tmp_claude):
    make_job(tmp_claude["jobs"], "job-aaa", SAMPLE_STATE)
    make_job(tmp_claude["jobs"], "job-bbb", SAMPLE_STATE_BG)
    resp = client.get("/api/jobs")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    ids = {j["id"] for j in body["jobs"]}
    assert "job-aaa" in ids
    assert "job-bbb" in ids


def test_get_jobs_limit(client, tmp_claude):
    for i in range(5):
        make_job(tmp_claude["jobs"], f"job-{i}", SAMPLE_STATE)
    resp = client.get("/api/jobs?limit=2")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["jobs"]) == 2
    assert body["total"] == 5


def test_get_jobs_project_filter(client, tmp_claude):
    make_job(tmp_claude["jobs"], "job-aaa", SAMPLE_STATE)
    other = {**SAMPLE_STATE, "cwd": "/home/user/otherproject"}
    make_job(tmp_claude["jobs"], "job-bbb", other)
    resp = client.get("/api/jobs?project=home-user-myproject")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["jobs"][0]["id"] == "job-aaa"


def test_get_job_detail_not_found(client):
    resp = client.get("/api/jobs/nonexistent")
    assert resp.status_code == 404


def test_get_job_detail_no_jsonl(client, tmp_claude):
    make_job(tmp_claude["jobs"], "job-aaa", SAMPLE_STATE)
    resp = client.get("/api/jobs/job-aaa")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == "job-aaa"
    assert body["tokens"] == 1234
    assert body["usage"] is None
    assert body["agents"] == []


def test_get_job_detail_with_usage(client, tmp_claude):
    make_job(
        tmp_claude["jobs"], "job-aaa", SAMPLE_STATE,
        jsonl_content=SAMPLE_JSONL, projects_dir=tmp_claude["projects"]
    )
    resp = client.get("/api/jobs/job-aaa")
    assert resp.status_code == 200
    body = resp.json()
    usage = body["usage"]
    assert usage is not None
    assert usage["input_tokens"] == 110
    assert usage["output_tokens"] == 55
    assert usage["cache_creation_input_tokens"] == 220
    assert usage["api_call_count"] == 2


def test_get_job_detail_with_agents(client, tmp_claude):
    make_job(
        tmp_claude["jobs"], "job-aaa", SAMPLE_STATE,
        jsonl_content=SAMPLE_JSONL, metas=[SAMPLE_META],
        projects_dir=tmp_claude["projects"]
    )
    resp = client.get("/api/jobs/job-aaa")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["agents"]) == 1
    assert body["agents"][0]["agent_type"] == "venue-scout"


def test_get_job_model_from_flags(client, tmp_claude):
    make_job(tmp_claude["jobs"], "job-bg", SAMPLE_STATE_BG)
    resp = client.get("/api/jobs/job-bg")
    assert resp.status_code == 200
    assert resp.json()["model"] == "claude-sonnet-4-6"


def test_get_job_model_none_for_main(client, tmp_claude):
    make_job(tmp_claude["jobs"], "job-main", SAMPLE_STATE)
    resp = client.get("/api/jobs/job-main")
    assert resp.status_code == 200
    assert resp.json()["model"] is None


def test_live_job_not_found(client):
    resp = client.post("/api/jobs/live", json={"job_id": "nonexistent"})
    assert resp.status_code == 404


# --- Chat session endpoint tests ---

def test_get_jobs_includes_chat_sessions(client, tmp_claude):
    make_job(tmp_claude["jobs"], "job-aaa", SAMPLE_STATE)
    _make_chat_session(tmp_claude["projects"], "-proj", "chat-uuid-1", CHAT_JSONL)
    resp = client.get("/api/jobs")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    ids = {j["id"] for j in body["jobs"]}
    assert "job-aaa" in ids
    assert "chat-uuid-1" in ids


def test_get_jobs_chat_source_field(client, tmp_claude):
    _make_chat_session(tmp_claude["projects"], "-proj", "chat-uuid-1", CHAT_JSONL)
    resp = client.get("/api/jobs")
    assert resp.status_code == 200
    jobs = resp.json()["jobs"]
    assert jobs[0]["source"] == "chat"


def test_get_jobs_background_source_field(client, tmp_claude):
    make_job(tmp_claude["jobs"], "job-aaa", SAMPLE_STATE)
    resp = client.get("/api/jobs")
    assert resp.status_code == 200
    jobs = resp.json()["jobs"]
    assert jobs[0]["source"] == "job"


def test_get_job_detail_chat_session(client, tmp_claude):
    _make_chat_session(
        tmp_claude["projects"], "-home-user-myproject", "chat-uuid-99", CHAT_JSONL
    )
    resp = client.get("/api/jobs/chat-uuid-99")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == "chat-uuid-99"
    assert body["source"] == "chat"
    assert body["template"] == "chat"
    assert body["state"] == "done"
    assert body["name"] == "Help me plan an event"
    assert body["usage"] is not None
    assert body["usage"]["api_call_count"] == 1
    assert body["agents"] == []


def test_get_job_detail_chat_tokens_correct(client, tmp_claude):
    _make_chat_session(tmp_claude["projects"], "-proj", "chat-uuid-99", CHAT_JSONL)
    resp = client.get("/api/jobs/chat-uuid-99")
    body = resp.json()
    expected = 40 + 15 + 80 + 160
    assert body["tokens"] == expected
    assert body["usage"]["total_tokens"] == expected

import json
from pathlib import Path

import pytest

from api.services.token_reader import (
    _extract_model,
    _parse_jsonl_usage,
    _parse_chat_jsonl,
    _session_name,
    _load_agent_metas,
    list_jobs,
    list_project_sessions,
    get_job_detail,
)
from api.tests.conftest import SAMPLE_JSONL, SAMPLE_META, SAMPLE_STATE, SAMPLE_STATE_BG, make_job


CHAT_JSONL_STRING_CONTENT = "\n".join([
    json.dumps({"type": "human", "message": {"content": "Plan my corporate dinner"}}),
    json.dumps({
        "type": "assistant",
        "message": {
            "model": "claude-sonnet-4-6",
            "usage": {
                "input_tokens": 50,
                "output_tokens": 20,
                "cache_creation_input_tokens": 100,
                "cache_read_input_tokens": 200,
            },
        },
    }),
])

CHAT_JSONL_LIST_CONTENT = "\n".join([
    json.dumps({
        "type": "human",
        "message": {
            "content": [
                {"type": "text", "text": "Find me a venue in Paris"},
                {"type": "image", "source": {}},
            ]
        },
    }),
    json.dumps({
        "type": "assistant",
        "message": {
            "model": "claude-sonnet-4-6",
            "usage": {
                "input_tokens": 30,
                "output_tokens": 10,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
            },
        },
    }),
])


def test_extract_model_present():
    flags = ["--permission-mode", "default", "--model", "claude-sonnet-4-6"]
    assert _extract_model(flags) == "claude-sonnet-4-6"


def test_extract_model_absent():
    flags = ["--agent", "claude", "--permission-mode", "auto"]
    assert _extract_model(flags) is None


def test_parse_jsonl_usage_sums(tmp_path):
    jsonl = tmp_path / "session.jsonl"
    jsonl.write_text(SAMPLE_JSONL)
    usage = _parse_jsonl_usage(jsonl)
    assert usage is not None
    assert usage.input_tokens == 110
    assert usage.output_tokens == 55
    assert usage.cache_creation_input_tokens == 220
    assert usage.cache_read_input_tokens == 330
    assert usage.total_tokens == 110 + 55 + 220 + 330
    assert usage.api_call_count == 2


def test_parse_jsonl_usage_missing_file(tmp_path):
    assert _parse_jsonl_usage(tmp_path / "nope.jsonl") is None


def test_parse_jsonl_usage_malformed_line(tmp_path):
    jsonl = tmp_path / "session.jsonl"
    jsonl.write_text("not json\n" + json.dumps({
        "type": "assistant",
        "message": {"usage": {"input_tokens": 5, "output_tokens": 3,
                               "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}},
    }))
    usage = _parse_jsonl_usage(jsonl)
    assert usage is not None
    assert usage.input_tokens == 5


def test_load_agent_metas(tmp_path):
    sub_dir = tmp_path / "session123" / "subagents"
    sub_dir.mkdir(parents=True)
    (sub_dir / "agent-0000.meta.json").write_text(SAMPLE_META)
    jsonl_path = tmp_path / "session123.jsonl"
    jsonl_path.touch()
    metas = _load_agent_metas(jsonl_path)
    assert len(metas) == 1
    assert metas[0].agent_type == "venue-scout"
    assert metas[0].spawn_depth == 1


def test_list_jobs_empty(tmp_claude):
    result = list_jobs()
    assert result.total == 0
    assert result.jobs == []


def test_list_jobs_returns_jobs(tmp_claude):
    make_job(tmp_claude["jobs"], "job-abc", SAMPLE_STATE)
    make_job(tmp_claude["jobs"], "job-def", SAMPLE_STATE_BG)
    result = list_jobs()
    assert result.total == 2
    ids = {j.id for j in result.jobs}
    assert "job-abc" in ids
    assert "job-def" in ids


def test_list_jobs_filter_project(tmp_claude):
    make_job(tmp_claude["jobs"], "job-abc", SAMPLE_STATE)
    other = {**SAMPLE_STATE, "cwd": "/home/user/otherproject"}
    make_job(tmp_claude["jobs"], "job-xyz", other)
    result = list_jobs(project="myproject")
    assert result.total == 1
    assert result.jobs[0].id == "job-abc"


def test_list_jobs_limit(tmp_claude):
    for i in range(10):
        make_job(tmp_claude["jobs"], f"job-{i:03}", SAMPLE_STATE)
    result = list_jobs(limit=3)
    assert len(result.jobs) == 3
    assert result.total == 10


def test_get_job_detail_not_found(tmp_claude):
    assert get_job_detail("nonexistent") is None


def test_get_job_detail_with_jsonl(tmp_claude):
    make_job(
        tmp_claude["jobs"], "job-abc", SAMPLE_STATE,
        jsonl_content=SAMPLE_JSONL, projects_dir=tmp_claude["projects"]
    )
    detail = get_job_detail("job-abc")
    assert detail is not None
    assert detail.usage is not None
    assert detail.tokens == detail.usage.total_tokens
    assert detail.usage.api_call_count == 2


def test_get_job_detail_with_agents(tmp_claude):
    make_job(
        tmp_claude["jobs"], "job-abc", SAMPLE_STATE,
        jsonl_content=SAMPLE_JSONL, metas=[SAMPLE_META],
        projects_dir=tmp_claude["projects"]
    )
    detail = get_job_detail("job-abc")
    assert len(detail.agents) == 1
    assert detail.agents[0].agent_type == "venue-scout"


# --- Chat / project session tests ---

def test_parse_chat_jsonl_string_content(tmp_path):
    jsonl = tmp_path / "sess.jsonl"
    jsonl.write_text(CHAT_JSONL_STRING_CONTENT)
    usage, model = _parse_chat_jsonl(jsonl)
    assert usage is not None
    assert usage.input_tokens == 50
    assert usage.output_tokens == 20
    assert usage.cache_creation_input_tokens == 100
    assert usage.cache_read_input_tokens == 200
    assert usage.total_tokens == 50 + 20 + 100 + 200
    assert usage.api_call_count == 1
    assert model == "claude-sonnet-4-6"


def test_parse_chat_jsonl_list_content(tmp_path):
    jsonl = tmp_path / "sess.jsonl"
    jsonl.write_text(CHAT_JSONL_LIST_CONTENT)
    usage, model = _parse_chat_jsonl(jsonl)
    assert usage is not None
    assert usage.input_tokens == 30
    assert model == "claude-sonnet-4-6"


def test_parse_chat_jsonl_no_assistant_turns(tmp_path):
    jsonl = tmp_path / "sess.jsonl"
    jsonl.write_text(json.dumps({"type": "human", "message": {"content": "hi"}}))
    usage, model = _parse_chat_jsonl(jsonl)
    assert usage is None
    assert model is None


def test_session_name_string(tmp_path):
    jsonl = tmp_path / "sess.jsonl"
    jsonl.write_text(CHAT_JSONL_STRING_CONTENT)
    assert _session_name(jsonl) == "Plan my corporate dinner"


def test_session_name_list(tmp_path):
    jsonl = tmp_path / "sess.jsonl"
    jsonl.write_text(CHAT_JSONL_LIST_CONTENT)
    assert _session_name(jsonl) == "Find me a venue in Paris"


def test_session_name_truncates_at_60(tmp_path):
    long_text = "A" * 80
    jsonl = tmp_path / "sess.jsonl"
    jsonl.write_text(json.dumps({"type": "human", "message": {"content": long_text}}))
    assert _session_name(jsonl) == "A" * 60


def _make_chat_session(projects_dir: Path, project: str, session_id: str, content: str):
    import os
    proj_dir = projects_dir / project
    proj_dir.mkdir(exist_ok=True)
    p = proj_dir / f"{session_id}.jsonl"
    p.write_text(content)
    os.utime(p, (1_000_000, 1_000_000))  # far past → state == "done"


def test_list_project_sessions_returns_sessions(tmp_claude):
    _make_chat_session(
        tmp_claude["projects"], "-home-user-myproject",
        "aaaa-1111", CHAT_JSONL_STRING_CONTENT
    )
    sessions = list_project_sessions()
    assert len(sessions) == 1
    s = sessions[0]
    assert s.id == "aaaa-1111"
    assert s.source == "chat"
    assert s.template == "chat"
    assert s.state == "done"
    assert s.tokens > 0
    assert s.model == "claude-sonnet-4-6"
    assert s.project == "home-user-myproject"


def test_list_project_sessions_skips_no_api_calls(tmp_claude):
    proj_dir = tmp_claude["projects"] / "-proj"
    proj_dir.mkdir()
    (proj_dir / "empty.jsonl").write_text(
        json.dumps({"type": "human", "message": {"content": "hi"}})
    )
    sessions = list_project_sessions()
    assert sessions == []


def test_list_project_sessions_project_filter(tmp_claude):
    _make_chat_session(
        tmp_claude["projects"], "-proj-a", "aaaa-1111", CHAT_JSONL_STRING_CONTENT
    )
    _make_chat_session(
        tmp_claude["projects"], "-proj-b", "bbbb-2222", CHAT_JSONL_STRING_CONTENT
    )
    sessions = list_project_sessions(project_filter="proj-a")
    assert len(sessions) == 1
    assert sessions[0].id == "aaaa-1111"


def test_list_jobs_includes_chat_sessions(tmp_claude):
    make_job(tmp_claude["jobs"], "job-abc", SAMPLE_STATE)
    _make_chat_session(
        tmp_claude["projects"], "-proj", "chat-uuid-1", CHAT_JSONL_STRING_CONTENT
    )
    result = list_jobs()
    assert result.total == 2
    ids = {j.id for j in result.jobs}
    assert "job-abc" in ids
    assert "chat-uuid-1" in ids


def test_list_jobs_source_field(tmp_claude):
    make_job(tmp_claude["jobs"], "job-abc", SAMPLE_STATE)
    _make_chat_session(
        tmp_claude["projects"], "-proj", "chat-uuid-1", CHAT_JSONL_STRING_CONTENT
    )
    result = list_jobs()
    by_id = {j.id: j for j in result.jobs}
    assert by_id["job-abc"].source == "job"
    assert by_id["chat-uuid-1"].source == "chat"


def test_get_job_detail_chat_fallback(tmp_claude):
    _make_chat_session(
        tmp_claude["projects"], "-home-user-myproject",
        "chat-uuid-99", CHAT_JSONL_STRING_CONTENT
    )
    detail = get_job_detail("chat-uuid-99")
    assert detail is not None
    assert detail.source == "chat"
    assert detail.usage is not None
    assert detail.usage.api_call_count == 1
    assert detail.agents == []
    assert detail.project == "home-user-myproject"


def test_get_job_detail_not_found_in_chat(tmp_claude):
    assert get_job_detail("completely-unknown-id") is None

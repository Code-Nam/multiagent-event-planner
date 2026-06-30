"""Tests for POST /api/run/{agent}."""

import json
from typing import AsyncGenerator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.services.agent_runner import ALLOWED_AGENTS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _mock_stream_one_chunk_then_done(
    agent_name: str,
    message: str,
    context: dict | None = None,
) -> AsyncGenerator[str, None]:
    """Minimal mock: yields one chunk event then a done event."""
    yield f'event: chunk\ndata: {json.dumps({"text": "Hello from mock"})}\n\n'
    yield f'event: done\ndata: {json.dumps({"agent": agent_name})}\n\n'


async def _mock_stream_error(
    agent_name: str,
    message: str,
    context: dict | None = None,
) -> AsyncGenerator[str, None]:
    """Mock that yields an SSE error event."""
    payload = json.dumps({"message": "agent unavailable", "code": "AGENT_FAIL"})
    yield f"event: error\ndata: {payload}\n\n"


_VALID_REQUEST_BODY = {"message": "What venues are available in Paris?"}


class TestAgentAllowlist:
    def test_invalid_agent_name_returns_400(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/run/{agent} with an agent not in ALLOWED_AGENTS returns HTTP 400."""
        response = client.post(
            "/api/run/not-a-real-agent", json=_VALID_REQUEST_BODY
        )

        assert response.status_code == 400, (
            f"Expected 400 for invalid agent, got {response.status_code}"
        )

    def test_invalid_agent_error_body_is_informative(
        self, client: TestClient, tmp_project_root
    ):
        """400 response for an invalid agent includes the rejected name in detail."""
        response = client.post(
            "/api/run/evil-agent", json=_VALID_REQUEST_BODY
        )

        assert response.status_code == 400
        detail = response.json().get("detail", "")
        assert "evil-agent" in detail, (
            f"Expected rejected agent name in 400 detail, got: {detail!r}"
        )

    def test_arbitrary_path_traversal_agent_returns_400(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/run with a path-traversal-style name is rejected with 400."""
        response = client.post(
            "/api/run/../config", json=_VALID_REQUEST_BODY
        )

        # FastAPI may route this differently; the important thing is it is not 200
        assert response.status_code in (400, 404, 422), (
            f"Expected rejection status, got {response.status_code}"
        )

    def test_all_allowed_agents_pass_allowlist_check(
        self, client: TestClient, tmp_project_root
    ):
        """Every agent in ALLOWED_AGENTS passes the name check (not blocked at 400)."""
        for agent_name in ALLOWED_AGENTS:
            with patch(
                "api.routes.agents.stream_agent",
                side_effect=_mock_stream_one_chunk_then_done,
            ):
                response = client.post(
                    f"/api/run/{agent_name}", json=_VALID_REQUEST_BODY
                )
            assert response.status_code != 400, (
                f"Agent '{agent_name}' should be allowed but got 400"
            )


class TestAgentSSEStream:
    def test_valid_agent_returns_text_event_stream_content_type(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/run/{agent} with a valid agent returns content-type text/event-stream."""
        with patch(
            "api.routes.agents.stream_agent",
            side_effect=_mock_stream_one_chunk_then_done,
        ):
            response = client.post(
                "/api/run/venue-scout", json=_VALID_REQUEST_BODY
            )

        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "text/event-stream" in content_type, (
            f"Expected text/event-stream content-type, got: {content_type!r}"
        )

    def test_valid_agent_stream_contains_chunk_event(
        self, client: TestClient, tmp_project_root
    ):
        """SSE response body includes at least one 'event: chunk' line."""
        with patch(
            "api.routes.agents.stream_agent",
            side_effect=_mock_stream_one_chunk_then_done,
        ):
            response = client.post(
                "/api/run/venue-scout", json=_VALID_REQUEST_BODY
            )

        assert "event: chunk" in response.text, (
            f"Expected 'event: chunk' in SSE stream, got: {response.text!r}"
        )

    def test_valid_agent_stream_contains_done_event(
        self, client: TestClient, tmp_project_root
    ):
        """SSE response body ends with an 'event: done' line."""
        with patch(
            "api.routes.agents.stream_agent",
            side_effect=_mock_stream_one_chunk_then_done,
        ):
            response = client.post(
                "/api/run/venue-scout", json=_VALID_REQUEST_BODY
            )

        assert "event: done" in response.text, (
            f"Expected 'event: done' in SSE stream, got: {response.text!r}"
        )

    def test_valid_agent_chunk_data_is_valid_json(
        self, client: TestClient, tmp_project_root
    ):
        """Each 'data:' line in the chunk event contains valid JSON."""
        with patch(
            "api.routes.agents.stream_agent",
            side_effect=_mock_stream_one_chunk_then_done,
        ):
            response = client.post(
                "/api/run/venue-scout", json=_VALID_REQUEST_BODY
            )

        for line in response.text.splitlines():
            if line.startswith("data:"):
                payload_str = line[len("data:"):].strip()
                try:
                    parsed = json.loads(payload_str)
                except json.JSONDecodeError as exc:
                    pytest.fail(f"SSE data line is not valid JSON: {payload_str!r} — {exc}")
                assert isinstance(parsed, dict), (
                    f"SSE data payload should be a JSON object, got {type(parsed)}"
                )

    def test_valid_agent_chunk_event_contains_text_key(
        self, client: TestClient, tmp_project_root
    ):
        """The chunk event data payload contains a 'text' key."""
        with patch(
            "api.routes.agents.stream_agent",
            side_effect=_mock_stream_one_chunk_then_done,
        ):
            response = client.post(
                "/api/run/venue-scout", json=_VALID_REQUEST_BODY
            )

        lines = response.text.splitlines()
        chunk_data_lines = [
            line[len("data:"):].strip()
            for i, line in enumerate(lines)
            if line.startswith("data:") and i > 0 and lines[i - 1] == "event: chunk"
        ]
        assert len(chunk_data_lines) >= 1, "No data line found after 'event: chunk'"
        for data_line in chunk_data_lines:
            payload = json.loads(data_line)
            assert "text" in payload, (
                f"Chunk data payload missing 'text' key: {payload}"
            )

    def test_valid_agent_with_context_is_accepted(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/run/{agent} with an optional context dict is accepted (200)."""
        request_body = {
            "message": "Find a venue",
            "context": {"budget": "€10000", "area": "Paris 8e"},
        }
        with patch(
            "api.routes.agents.stream_agent",
            side_effect=_mock_stream_one_chunk_then_done,
        ):
            response = client.post("/api/run/venue-scout", json=request_body)

        assert response.status_code == 200

    def test_agent_stream_error_event_has_correct_structure(
        self, client: TestClient, tmp_project_root
    ):
        """When stream_agent yields an error event, the SSE body contains 'event: error'."""
        with patch(
            "api.routes.agents.stream_agent",
            side_effect=_mock_stream_error,
        ):
            response = client.post(
                "/api/run/venue-scout", json=_VALID_REQUEST_BODY
            )

        assert response.status_code == 200
        assert "event: error" in response.text, (
            f"Expected 'event: error' in SSE response, got: {response.text!r}"
        )

    def test_missing_message_field_returns_422(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/run/{agent} without a 'message' field returns HTTP 422."""
        response = client.post("/api/run/venue-scout", json={})

        assert response.status_code == 422

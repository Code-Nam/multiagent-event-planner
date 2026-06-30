"""Tests for GET /api/event and POST /api/event."""

import pytest
from fastapi.testclient import TestClient

from api.tests.conftest import BLANK_EVENT_CONTEXT, POPULATED_EVENT_CONTEXT


class TestGetEvent:
    def test_get_event_returns_event_context_shape(
        self, client: TestClient, tmp_project_root, monkeypatch
    ):
        """GET /api/event returns a JSON object with all EventContext fields."""
        response = client.get("/api/event")

        assert response.status_code == 200
        body = response.json()
        expected_fields = {
            "name",
            "date",
            "type",
            "expected_attendance",
            "fixed_budget",
            "event_lead",
            "preferred_area",
            "constraints",
        }
        assert expected_fields == set(body.keys()), (
            f"Response keys {set(body.keys())} do not match expected {expected_fields}"
        )

    def test_get_event_returns_populated_values(
        self, client: TestClient, tmp_project_root
    ):
        """GET /api/event returns the actual field values from event-context.md."""
        response = client.get("/api/event")

        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "Summer Gala 2026"
        assert body["date"] == "2026-08-15"
        assert body["type"] == "gala"
        assert body["fixed_budget"] == "€15000"
        assert body["event_lead"] == "Alice Dupont"

    def test_get_event_with_blank_template_returns_empty_strings(
        self, client: TestClient, tmp_project_root
    ):
        """GET /api/event with an unfilled template strips [TBD] tokens to empty strings.

        Note: fixed_budget uses the template value '€[TBD]' where the '€' prefix sits
        outside the bracket — _TBD_RE matches only bare '[*]' patterns, so fixed_budget
        returns '€[TBD]' unchanged.  All other fields with pure [TBD] values are stripped.
        """
        event_ctx = tmp_project_root / "event-context.md"
        event_ctx.write_text(BLANK_EVENT_CONTEXT, encoding="utf-8")

        response = client.get("/api/event")

        assert response.status_code == 200
        body = response.json()
        # All fields except fixed_budget should be empty (their template values are bare [TBD])
        fields_that_should_be_empty = {k for k in body if k != "fixed_budget"}
        for field in fields_that_should_be_empty:
            assert body[field] == "", (
                f"Field '{field}' expected empty string but got '{body[field]}'"
            )
        # fixed_budget keeps '€[TBD]' because the € prefix prevents TBD stripping
        assert body["fixed_budget"] == "€[TBD]", (
            f"Expected fixed_budget='€[TBD]' (prefix outside brackets), got '{body['fixed_budget']}'"
        )

    def test_get_event_tbd_values_become_empty_strings(
        self, client: TestClient, tmp_project_root
    ):
        """Values matching [*] pattern are normalised to empty string."""
        event_ctx = tmp_project_root / "event-context.md"
        event_ctx.write_text(BLANK_EVENT_CONTEXT, encoding="utf-8")

        response = client.get("/api/event")
        body = response.json()

        assert "[TBD]" not in body.values(), (
            "Raw [TBD] placeholders should be stripped to empty strings"
        )


class TestPostEvent:
    def _valid_payload(self) -> dict:
        return {
            "name": "Tech Summit 2026",
            "date": "2026-09-01",
            "type": "workshop",
            "expected_attendance": "150",
            "fixed_budget": "€8000",
            "event_lead": "Bob Martin",
            "preferred_area": "Paris 11e",
            "constraints": "Vegetarian catering only",
        }

    def test_post_event_with_valid_body_returns_ok(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/event with a complete EventContext body returns {"ok": true}."""
        response = client.post("/api/event", json=self._valid_payload())

        assert response.status_code == 200
        assert response.json() == {"ok": True}

    def test_post_event_persists_values(self, client: TestClient, tmp_project_root):
        """POST /api/event updates the file so a subsequent GET returns new values."""
        payload = self._valid_payload()
        client.post("/api/event", json=payload)

        get_response = client.get("/api/event")
        assert get_response.status_code == 200
        body = get_response.json()
        assert body["name"] == payload["name"]
        assert body["event_lead"] == payload["event_lead"]
        assert body["constraints"] == payload["constraints"]

    def test_post_event_with_missing_required_field_returns_422(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/event without a required field returns HTTP 422."""
        incomplete_payload = self._valid_payload()
        del incomplete_payload["name"]

        response = client.post("/api/event", json=incomplete_payload)

        assert response.status_code == 422

    def test_post_event_with_empty_body_returns_422(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/event with an empty body returns HTTP 422."""
        response = client.post("/api/event", json={})

        assert response.status_code == 422

"""Tests for GET /api/status."""

import pytest
from fastapi.testclient import TestClient

from api.tests.conftest import BLANK_EVENT_CONTEXT, SAMPLE_DRAFT_FRONTMATTER


class TestGetStatus:
    def test_status_returns_pipeline_status_shape(
        self, client: TestClient, tmp_project_root
    ):
        """GET /api/status returns a JSON object with all PipelineStatus fields."""
        response = client.get("/api/status")

        assert response.status_code == 200
        body = response.json()
        expected_fields = {
            "event_configured",
            "drafts_count",
            "doc_content_count",
            "output_count",
            "draft_names",
        }
        assert expected_fields == set(body.keys()), (
            f"PipelineStatus keys {set(body.keys())} differ from expected {expected_fields}"
        )

    def test_empty_project_has_zero_counts(self, client: TestClient, tmp_project_root):
        """GET /api/status on a project with no drafts/docs/output returns all counts as 0."""
        # The tmp_project_root fixture writes populated event-context.md
        # but leaves drafts/, doc-content/, output/ empty.
        response = client.get("/api/status")

        assert response.status_code == 200
        body = response.json()
        assert body["drafts_count"] == 0, (
            f"Expected drafts_count=0, got {body['drafts_count']}"
        )
        assert body["doc_content_count"] == 0, (
            f"Expected doc_content_count=0, got {body['doc_content_count']}"
        )
        assert body["output_count"] == 0, (
            f"Expected output_count=0, got {body['output_count']}"
        )

    def test_empty_project_draft_names_is_empty_list(
        self, client: TestClient, tmp_project_root
    ):
        """GET /api/status on a project with no drafts returns draft_names=[]."""
        response = client.get("/api/status")
        body = response.json()

        assert body["draft_names"] == [], (
            f"Expected empty draft_names list, got {body['draft_names']}"
        )

    def test_populated_event_context_sets_event_configured_true(
        self, client: TestClient, tmp_project_root
    ):
        """event_configured is True when event-context.md has at least one non-empty field."""
        # tmp_project_root writes POPULATED_EVENT_CONTEXT by default
        response = client.get("/api/status")
        body = response.json()

        assert body["event_configured"] is True, (
            "Expected event_configured=True with populated event-context.md"
        )

    def test_blank_event_context_sets_event_configured_true_due_to_budget_prefix(
        self, client: TestClient, tmp_project_root
    ):
        """event_configured is True even with a blank template because fixed_budget
        parses as '€[TBD]' — the € prefix sits outside the [*] pattern that file_store
        strips, so at least one field is non-empty and event_configured becomes True.
        """
        event_ctx = tmp_project_root / "event-context.md"
        event_ctx.write_text(BLANK_EVENT_CONTEXT, encoding="utf-8")

        response = client.get("/api/status")
        body = response.json()

        # The only non-empty field from the blank template is fixed_budget='€[TBD]'
        assert body["event_configured"] is True, (
            "Expected event_configured=True because fixed_budget='€[TBD]' is non-empty"
        )

    def test_drafts_count_matches_number_of_draft_files(
        self, client: TestClient, tmp_project_root
    ):
        """drafts_count reflects the number of .md files in drafts/."""
        drafts_dir = tmp_project_root / "drafts"
        for name in ("alpha", "beta", "gamma"):
            (drafts_dir / f"{name}.md").write_text(
                SAMPLE_DRAFT_FRONTMATTER, encoding="utf-8"
            )

        response = client.get("/api/status")
        body = response.json()

        assert body["drafts_count"] == 3, (
            f"Expected drafts_count=3, got {body['drafts_count']}"
        )

    def test_draft_names_lists_all_draft_stems(
        self, client: TestClient, tmp_project_root
    ):
        """draft_names contains the stem of every draft file."""
        drafts_dir = tmp_project_root / "drafts"
        for name in ("alpha", "beta"):
            (drafts_dir / f"{name}.md").write_text(
                SAMPLE_DRAFT_FRONTMATTER, encoding="utf-8"
            )

        response = client.get("/api/status")
        draft_names = response.json()["draft_names"]

        assert set(draft_names) == {"alpha", "beta"}, (
            f"Expected draft names alpha and beta, got {draft_names}"
        )

    def test_doc_content_count_reflects_json_files(
        self, client: TestClient, tmp_project_root
    ):
        """doc_content_count reflects the number of .json files in doc-content/."""
        doc_dir = tmp_project_root / "doc-content"
        (doc_dir / "budget-spec.json").write_text("{}", encoding="utf-8")
        (doc_dir / "venues-spec.json").write_text("{}", encoding="utf-8")

        response = client.get("/api/status")
        body = response.json()

        assert body["doc_content_count"] == 2, (
            f"Expected doc_content_count=2, got {body['doc_content_count']}"
        )

    def test_output_count_reflects_files_in_output_dir(
        self, client: TestClient, tmp_project_root
    ):
        """output_count reflects the number of files in output/."""
        out_dir = tmp_project_root / "output"
        (out_dir / "budget.xlsx").write_bytes(b"fake xlsx")
        (out_dir / "planning.docx").write_bytes(b"fake docx")

        response = client.get("/api/status")
        body = response.json()

        assert body["output_count"] == 2, (
            f"Expected output_count=2, got {body['output_count']}"
        )

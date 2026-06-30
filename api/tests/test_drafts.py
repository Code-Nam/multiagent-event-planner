"""Tests for GET /api/drafts and GET /api/drafts/{name}."""

import pytest
from fastapi.testclient import TestClient

from api.tests.conftest import SAMPLE_DRAFT_FRONTMATTER


def _write_draft(drafts_dir, name: str = "test-draft", content: str = SAMPLE_DRAFT_FRONTMATTER):
    """Helper: write a draft file and return its stem name."""
    path = drafts_dir / f"{name}.md"
    path.write_text(content, encoding="utf-8")
    return name


class TestListDrafts:
    def test_empty_drafts_directory_returns_empty_list(
        self, client: TestClient, tmp_project_root
    ):
        """GET /api/drafts with no files in drafts/ returns an empty JSON array."""
        response = client.get("/api/drafts")

        assert response.status_code == 200
        assert response.json() == [], (
            "Expected empty list when drafts/ directory is empty"
        )

    def test_single_draft_file_returns_one_summary(
        self, client: TestClient, tmp_project_root
    ):
        """GET /api/drafts with one draft file returns a list with one DraftSummary."""
        _write_draft(tmp_project_root / "drafts", "venue-inquiry")

        response = client.get("/api/drafts")

        assert response.status_code == 200
        items = response.json()
        assert len(items) == 1, f"Expected 1 draft, got {len(items)}"

    def test_draft_summary_contains_expected_fields(
        self, client: TestClient, tmp_project_root
    ):
        """Each DraftSummary includes name, purpose, to, subject, status."""
        _write_draft(tmp_project_root / "drafts", "venue-inquiry")

        response = client.get("/api/drafts")
        item = response.json()[0]

        expected_fields = {"name", "purpose", "to", "subject", "status"}
        assert expected_fields == set(item.keys()), (
            f"DraftSummary keys {set(item.keys())} do not match {expected_fields}"
        )

    def test_draft_summary_values_match_frontmatter(
        self, client: TestClient, tmp_project_root
    ):
        """DraftSummary values are parsed from YAML frontmatter."""
        _write_draft(tmp_project_root / "drafts", "venue-inquiry")

        response = client.get("/api/drafts")
        item = response.json()[0]

        assert item["name"] == "venue-inquiry"
        assert item["to"] == "venue@example.com"
        assert item["subject"] == "Inquiry"
        assert item["purpose"] == "venue_inquiry"
        assert item["status"] == "draft"

    def test_multiple_draft_files_returns_all_summaries(
        self, client: TestClient, tmp_project_root
    ):
        """GET /api/drafts with multiple files returns one summary per file."""
        drafts_dir = tmp_project_root / "drafts"
        _write_draft(drafts_dir, "draft-a")
        _write_draft(drafts_dir, "draft-b")
        _write_draft(drafts_dir, "draft-c")

        response = client.get("/api/drafts")

        assert response.status_code == 200
        assert len(response.json()) == 3, (
            f"Expected 3 drafts, got {len(response.json())}"
        )

    def test_draft_without_frontmatter_returns_empty_fields(
        self, client: TestClient, tmp_project_root
    ):
        """A draft without YAML frontmatter returns empty string fields."""
        _write_draft(
            tmp_project_root / "drafts",
            "no-frontmatter",
            content="Just plain body text, no frontmatter here.",
        )

        response = client.get("/api/drafts")

        assert response.status_code == 200
        item = response.json()[0]
        assert item["to"] == ""
        assert item["subject"] == ""
        assert item["purpose"] == ""


class TestGetDraft:
    def test_existing_draft_returns_draft_with_body(
        self, client: TestClient, tmp_project_root
    ):
        """GET /api/drafts/{name} for an existing file returns Draft including body."""
        _write_draft(tmp_project_root / "drafts", "venue-inquiry")

        response = client.get("/api/drafts/venue-inquiry")

        assert response.status_code == 200
        body = response.json()
        expected_fields = {"name", "purpose", "to", "subject", "status", "body"}
        assert expected_fields == set(body.keys()), (
            f"Draft keys {set(body.keys())} do not match {expected_fields}"
        )

    def test_existing_draft_body_content_is_correct(
        self, client: TestClient, tmp_project_root
    ):
        """GET /api/drafts/{name} returns the correct body text."""
        _write_draft(tmp_project_root / "drafts", "venue-inquiry")

        response = client.get("/api/drafts/venue-inquiry")

        assert response.json()["body"] == "Body text here."

    def test_existing_draft_frontmatter_fields_are_correct(
        self, client: TestClient, tmp_project_root
    ):
        """GET /api/drafts/{name} returns correct frontmatter fields."""
        _write_draft(tmp_project_root / "drafts", "venue-inquiry")

        response = client.get("/api/drafts/venue-inquiry")
        data = response.json()

        assert data["to"] == "venue@example.com"
        assert data["subject"] == "Inquiry"
        assert data["purpose"] == "venue_inquiry"
        assert data["status"] == "draft"

    def test_missing_draft_returns_404(self, client: TestClient, tmp_project_root):
        """GET /api/drafts/{name} for a non-existent file returns HTTP 404."""
        response = client.get("/api/drafts/does-not-exist")

        assert response.status_code == 404

    def test_missing_draft_error_body_references_name(
        self, client: TestClient, tmp_project_root
    ):
        """404 response detail string mentions the requested draft name."""
        response = client.get("/api/drafts/ghost-draft")

        assert response.status_code == 404
        detail = response.json().get("detail", "")
        assert "ghost-draft" in detail, (
            f"Expected draft name in 404 detail, got: {detail!r}"
        )

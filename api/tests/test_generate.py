"""Tests for POST /api/generate/{xlsx|docx|ppt} and POST /api/gmail-draft."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from api.models import GenerateResult


_OK_RESULT = GenerateResult(ok=True, path="output/test.xlsx")
_FAIL_RESULT = GenerateResult(ok=False, error="script failed")


class TestGenerateXlsx:
    def test_generate_xlsx_returns_200_on_success(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/generate/xlsx returns HTTP 200 when script succeeds."""
        with patch("api.routes.generate.run_script", return_value=_OK_RESULT):
            response = client.post("/api/generate/xlsx", json={})

        assert response.status_code == 200

    def test_generate_xlsx_returns_ok_true_on_success(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/generate/xlsx response body has ok=true when script succeeds."""
        with patch("api.routes.generate.run_script", return_value=_OK_RESULT):
            response = client.post("/api/generate/xlsx", json={})

        body = response.json()
        assert body["ok"] is True, f"Expected ok=true, got {body}"

    def test_generate_xlsx_returns_path_on_success(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/generate/xlsx response body includes the output path."""
        with patch("api.routes.generate.run_script", return_value=_OK_RESULT):
            response = client.post("/api/generate/xlsx", json={})

        assert response.json()["path"] == "output/test.xlsx"

    def test_generate_xlsx_returns_200_on_script_failure(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/generate/xlsx returns HTTP 200 even when the script fails."""
        with patch("api.routes.generate.run_script", return_value=_FAIL_RESULT):
            response = client.post("/api/generate/xlsx", json={})

        assert response.status_code == 200

    def test_generate_xlsx_returns_ok_false_on_script_failure(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/generate/xlsx response has ok=false and error text when script fails."""
        with patch("api.routes.generate.run_script", return_value=_FAIL_RESULT):
            response = client.post("/api/generate/xlsx", json={})

        body = response.json()
        assert body["ok"] is False, f"Expected ok=false, got {body}"
        assert body["error"] == "script failed"

    def test_generate_xlsx_calls_run_script_with_correct_script_name(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/generate/xlsx invokes run_script with 'generate-xlsx.py'."""
        with patch("api.routes.generate.run_script", return_value=_OK_RESULT) as mock_run:
            client.post("/api/generate/xlsx", json={})

        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == "generate-xlsx.py"

    def test_generate_xlsx_passes_extra_args_when_provided(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/generate/xlsx forwards --input and --output to run_script."""
        with patch("api.routes.generate.run_script", return_value=_OK_RESULT) as mock_run:
            client.post(
                "/api/generate/xlsx",
                json={"input": "doc-content/spec.json", "output": "output/budget.xlsx"},
            )

        call_args = mock_run.call_args[0]
        assert "--input" in call_args
        assert "doc-content/spec.json" in call_args
        assert "--output" in call_args
        assert "output/budget.xlsx" in call_args


class TestGenerateDocx:
    def test_generate_docx_returns_200_on_success(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/generate/docx returns HTTP 200 when script succeeds."""
        with patch("api.routes.generate.run_script", return_value=_OK_RESULT):
            response = client.post("/api/generate/docx", json={})

        assert response.status_code == 200

    def test_generate_docx_calls_correct_script(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/generate/docx invokes run_script with 'generate-docx.py'."""
        with patch("api.routes.generate.run_script", return_value=_OK_RESULT) as mock_run:
            client.post("/api/generate/docx", json={})

        assert mock_run.call_args[0][0] == "generate-docx.py"


class TestGeneratePpt:
    def test_generate_ppt_returns_200_on_success(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/generate/ppt returns HTTP 200 when script succeeds."""
        with patch("api.routes.generate.run_script", return_value=_OK_RESULT):
            response = client.post("/api/generate/ppt", json={})

        assert response.status_code == 200

    def test_generate_ppt_calls_correct_script(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/generate/ppt invokes run_script with 'generate-ppt.py'."""
        with patch("api.routes.generate.run_script", return_value=_OK_RESULT) as mock_run:
            client.post("/api/generate/ppt", json={})

        assert mock_run.call_args[0][0] == "generate-ppt.py"


class TestGmailDraft:
    def test_gmail_draft_returns_200_on_success(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/gmail-draft returns HTTP 200 when script succeeds."""
        result = GenerateResult(ok=True, path="gmail://draft/abc123")
        with patch("api.routes.generate.run_script", return_value=result):
            response = client.post("/api/gmail-draft", json={})

        assert response.status_code == 200

    def test_gmail_draft_returns_ok_true_on_success(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/gmail-draft response has ok=true when script succeeds."""
        result = GenerateResult(ok=True, path="gmail://draft/abc123")
        with patch("api.routes.generate.run_script", return_value=result):
            response = client.post("/api/gmail-draft", json={})

        assert response.json()["ok"] is True

    def test_gmail_draft_calls_correct_script(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/gmail-draft invokes run_script with 'gmail-draft.py'."""
        result = GenerateResult(ok=True)
        with patch("api.routes.generate.run_script", return_value=result) as mock_run:
            client.post("/api/gmail-draft", json={})

        assert mock_run.call_args[0][0] == "gmail-draft.py"

    def test_gmail_draft_returns_200_on_failure(
        self, client: TestClient, tmp_project_root
    ):
        """POST /api/gmail-draft returns HTTP 200 even when script fails (ok=false in body)."""
        with patch("api.routes.generate.run_script", return_value=_FAIL_RESULT):
            response = client.post("/api/gmail-draft", json={})

        assert response.status_code == 200
        assert response.json()["ok"] is False

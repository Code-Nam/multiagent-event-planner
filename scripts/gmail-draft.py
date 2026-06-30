"""
gmail-draft.py — AGEVP Phase 2

Reads a markdown draft file with YAML frontmatter (to:, subject:) and
creates a Gmail draft via the Gmail API OAuth2 flow. Never sends email.

Usage:
    python scripts/gmail-draft.py [--draft drafts/<purpose>-<date>.md]

Draft file format:
    ---
    to: recipient@example.com
    subject: Email subject
    purpose: venue_inquiry
    status: draft
    ---

    Email body here...

Credentials:
    Place scripts/credentials.json (OAuth2 Desktop client secrets) before
    running. On first run a browser window opens for consent; the resulting
    token is stored in scripts/token.json for subsequent runs.
"""

import sys
import json
import base64
import argparse
from email.mime.text import MIMEText
from pathlib import Path

CREDENTIALS_PATH = Path(__file__).parent / "credentials.json"
TOKEN_PATH = Path(__file__).parent / "token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

_CREDENTIAL_GUARD_MSG = """\
ERROR: scripts/credentials.json not found.
To set up Gmail API:
1. Go to https://console.cloud.google.com/
2. Enable Gmail API
3. Create OAuth2 credentials (Desktop app)
4. Download as credentials.json -> scripts/credentials.json"""


def _check_credentials() -> None:
    """Exit with instructions if credentials.json is absent."""
    if not CREDENTIALS_PATH.exists():
        print(_CREDENTIAL_GUARD_MSG, file=sys.stderr)
        sys.exit(1)


def _load_gmail_service():
    """
    Authenticate via OAuth2 and return an authorised Gmail API service object.

    Uses cached token.json when available; launches the browser OAuth consent
    flow on first run.
    """
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        print("Missing dependency. Run: pip install -r scripts/requirements.txt", file=sys.stderr)
        sys.exit(1)

    creds = None

    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        except Exception as exc:
            print(f"WARNING: could not load token.json ({exc}); re-authenticating.", file=sys.stderr)
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as exc:
                print(f"WARNING: token refresh failed ({exc}); re-authenticating.", file=sys.stderr)
                creds = None

        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)

        try:
            TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
        except OSError as exc:
            print(f"WARNING: could not save token.json: {exc}", file=sys.stderr)

    try:
        service = build("gmail", "v1", credentials=creds)
    except Exception as exc:
        print(f"ERROR: failed to build Gmail service: {exc}", file=sys.stderr)
        sys.exit(1)

    return service


def _parse_draft_markdown(draft_path: Path) -> tuple[str, str, str]:
    """
    Parse a markdown draft file with YAML frontmatter.

    Args:
        draft_path: Path to the .md draft file.

    Returns:
        Tuple of (to_address, subject, body).

    Raises:
        SystemExit: on missing file, bad format, or missing required fields.
    """
    try:
        import yaml
    except ImportError:
        print("Missing dependency. Run: pip install -r scripts/requirements.txt", file=sys.stderr)
        sys.exit(1)

    try:
        content = draft_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: cannot read {draft_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    if not content.startswith("---"):
        print(f"ERROR: {draft_path} does not begin with YAML frontmatter (---)", file=sys.stderr)
        sys.exit(1)

    parts = content.split("---", maxsplit=2)
    if len(parts) < 3:
        print(f"ERROR: {draft_path} has malformed YAML frontmatter (missing closing ---)", file=sys.stderr)
        sys.exit(1)

    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        print(f"ERROR: YAML parse error in {draft_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(frontmatter, dict):
        print(f"ERROR: frontmatter in {draft_path} is not a mapping", file=sys.stderr)
        sys.exit(1)

    to_address: str = frontmatter.get("to", "")
    subject: str = frontmatter.get("subject", "")
    body: str = parts[2].strip()

    if not to_address:
        print(f"ERROR: 'to:' field missing or empty in {draft_path}", file=sys.stderr)
        sys.exit(1)
    if not subject:
        print(f"ERROR: 'subject:' field missing or empty in {draft_path}", file=sys.stderr)
        sys.exit(1)

    return to_address, subject, body


def _latest_draft_file(drafts_dir: Path) -> Path:
    """
    Return the most recently modified .md file in drafts_dir.

    Raises:
        SystemExit: if no .md files are found.
    """
    md_files = sorted(drafts_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not md_files:
        print(f"ERROR: no .md files found in {drafts_dir}", file=sys.stderr)
        sys.exit(1)
    return md_files[0]


def create_gmail_draft(draft_path: Path) -> str:
    """
    Parse a markdown draft file and create a Gmail draft via the API.

    Args:
        draft_path: Path to the .md file with YAML frontmatter.

    Returns:
        The Gmail draft ID string.

    Raises:
        SystemExit: on authentication or API errors.
    """
    _check_credentials()

    to_address, subject, body = _parse_draft_markdown(draft_path)

    service = _load_gmail_service()

    mime_message = MIMEText(body, "plain", "utf-8")
    mime_message["to"] = to_address
    mime_message["subject"] = subject

    raw_bytes = base64.urlsafe_b64encode(mime_message.as_bytes()).decode("utf-8")
    draft_body = {"message": {"raw": raw_bytes}}

    try:
        result = service.users().drafts().create(userId="me", body=draft_body).execute()
    except Exception as exc:
        print(f"ERROR: Gmail API call failed: {exc}", file=sys.stderr)
        sys.exit(1)

    draft_id: str = result.get("id", "")
    return draft_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a Gmail draft from a markdown file with YAML frontmatter."
    )
    parser.add_argument(
        "--draft",
        default=None,
        help="Path to the draft .md file (default: latest file in drafts/)",
    )
    args = parser.parse_args()

    if args.draft:
        target = Path(args.draft)
    else:
        repo_root = Path(__file__).parent.parent
        target = _latest_draft_file(repo_root / "drafts")

    draft_id = create_gmail_draft(target)
    print(f"Draft created: {draft_id}")
    sys.exit(0)

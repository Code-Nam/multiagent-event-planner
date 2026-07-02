#!/usr/bin/env python3
"""Push a draft markdown file to Gmail as a draft (never sends)."""

import base64
import os
import sys
from email.header import Header
from email.mime.text import MIMEText

import yaml
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(os.path.dirname(SCRIPT_DIR), ".env"))
CREDENTIALS_PATH = os.path.join(SCRIPT_DIR, "credentials.json")
TOKEN_PATH = os.path.join(SCRIPT_DIR, "token.json")


def authenticate():
    if not os.path.exists(CREDENTIALS_PATH):
        print(
            "Missing scripts/credentials.json. "
            "Obtain an OAuth 2.0 Client ID (Desktop app) from Google Cloud Console "
            "and save it here.",
            file=sys.stderr,
        )
        sys.exit(1)

    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return creds


def parse_draft(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        raise ValueError("Draft missing YAML frontmatter (expected leading ---)")

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Draft frontmatter not closed with ---")

    frontmatter = yaml.safe_load(parts[1])
    body = parts[2].strip()

    raw_to = frontmatter.get("to")
    # YAML parses `[To complete]` as a list — coerce to string
    if isinstance(raw_to, list):
        raw_to = ", ".join(str(x) for x in raw_to)
    elif raw_to is not None:
        raw_to = str(raw_to).strip()

    # Treat template placeholder as absent (handles both bare and bracketed forms)
    PLACEHOLDER_MARKERS = {"[to complete]", "[à compléter]", "to complete", "à compléter", ""}
    if not raw_to or raw_to.lower() in PLACEHOLDER_MARKERS:
        raw_to = None

    to = raw_to or os.environ.get("GMAIL_TO") or "annampierretran@gmail.com"
    subject = frontmatter.get("subject")
    if not subject:
        raise ValueError("Frontmatter must include 'subject'")

    return to, subject, body


def create_draft(service, to: str, subject: str, body: str) -> str:
    message = MIMEText(body, "plain", "utf-8")
    message["to"] = to
    # RFC2047-encode subject so non-ASCII chars (em-dash, accents) are safe
    message["subject"] = Header(subject, "utf-8")
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    draft = service.users().drafts().create(
        userId="me", body={"message": {"raw": raw}}
    ).execute()

    return draft["id"]


def delete_draft(service, draft_id: str) -> None:
    """Delete a Gmail draft by ID. Silently ignores 404 (already gone)."""
    try:
        service.users().drafts().delete(userId="me", id=draft_id).execute()
        print(f"Draft deleted: {draft_id}")
    except Exception as exc:
        if "404" in str(exc) or "notFound" in str(exc):
            print(f"Draft {draft_id} not found (already deleted or invalid)", file=sys.stderr)
        else:
            raise


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Push a markdown draft to Gmail (never sends)."
    )
    parser.add_argument("draft_path", help="Path to the draft markdown file")
    parser.add_argument(
        "--delete-draft",
        metavar="DRAFT_ID",
        help="Delete this Gmail draft ID before creating the new one",
    )
    args = parser.parse_args()

    if not os.path.exists(args.draft_path):
        print(f"Draft file not found: {args.draft_path}", file=sys.stderr)
        sys.exit(1)

    creds = authenticate()
    service = build("gmail", "v1", credentials=creds)

    if args.delete_draft:
        delete_draft(service, args.delete_draft)

    to, subject, body = parse_draft(args.draft_path)
    draft_id = create_draft(service, to, subject, body)
    print(f"Draft created: {draft_id}")


if __name__ == "__main__":
    main()

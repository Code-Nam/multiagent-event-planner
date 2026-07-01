#!/usr/bin/env python3
"""Push a draft markdown file to Gmail as a draft (never sends)."""

import base64
import os
import sys
from email.mime.text import MIMEText

import yaml
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
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

    to = frontmatter.get("to") or os.environ.get("GMAIL_TO")
    subject = frontmatter.get("subject")
    if not to:
        raise ValueError("No recipient: set 'to' in frontmatter or GMAIL_TO env var")
    if not subject:
        raise ValueError("Frontmatter must include 'subject'")

    return to, subject, body


def create_draft(service, to, subject, body):
    message = MIMEText(body, "plain", "utf-8")
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    draft = service.users().drafts().create(
        userId="me", body={"message": {"raw": raw}}
    ).execute()

    return draft["id"]


def main():
    if len(sys.argv) != 2:
        print("Usage: python gmail_draft.py <draft-path>", file=sys.stderr)
        sys.exit(1)

    draft_path = sys.argv[1]
    if not os.path.exists(draft_path):
        print(f"Draft file not found: {draft_path}", file=sys.stderr)
        sys.exit(1)

    creds = authenticate()
    service = build("gmail", "v1", credentials=creds)

    to, subject, body = parse_draft(draft_path)
    draft_id = create_draft(service, to, subject, body)
    print(f"Draft created: {draft_id}")


if __name__ == "__main__":
    main()

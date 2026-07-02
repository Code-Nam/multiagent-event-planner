#!/usr/bin/env python3
"""Upload output/ files to Google Drive under an event-named folder.

Usage:
    python scripts/gdrive_upload.py [files/globs ...] [--folder <name>]

Without arguments every file in output/ goes to one folder named after the
event (GDRIVE_FOLDER env or event-context.md). Pass files or globs (resolved
against the CWD, then output/) to upload a subset, and --folder to name the
Drive folder explicitly — one run per destination folder.
"""

import argparse
import glob
import os
import re
import sys

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

load_dotenv(os.path.join(ROOT_DIR, ".env"))

CREDENTIALS_PATH = os.path.join(SCRIPT_DIR, "credentials.json")
TOKEN_PATH = os.path.join(SCRIPT_DIR, "gdrive_token.json")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")
EVENT_CONTEXT_PATH = os.path.join(ROOT_DIR, "event-context.md")

MIME_TYPES = {
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".pdf": "application/pdf",
    ".md": "text/markdown",
}


def authenticate() -> Credentials:
    if not os.path.exists(CREDENTIALS_PATH):
        print(
            "Missing scripts/credentials.json. "
            "Obtain an OAuth 2.0 Client ID (Desktop app) from Google Cloud Console "
            "and save it as scripts/credentials.json.",
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


def get_event_name() -> str:
    if not os.path.exists(EVENT_CONTEXT_PATH):
        return "AGEVP-output"
    with open(EVENT_CONTEXT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            m = re.search(r"\*\*Name:\*\*\s*(.+)", line)
            if m:
                name = m.group(1).strip()
                if name and name != "[TBD]":
                    return name
    return "AGEVP-output"


def find_or_create_folder(service: Resource, name: str) -> str:
    query = (
        f"name='{name}' and mimeType='application/vnd.google-apps.folder' "
        "and trashed=false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]

    meta = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    folder = service.files().create(body=meta, fields="id").execute()
    return folder["id"]


def upload_file(service: Resource, path: str, folder_id: str) -> str:
    name = os.path.basename(path)
    ext = os.path.splitext(name)[1].lower()
    mime = MIME_TYPES.get(ext, "application/octet-stream")

    meta = {"name": name, "parents": [folder_id]}
    media = MediaFileUpload(path, mimetype=mime, resumable=True)

    result = service.files().create(
        body=meta,
        media_body=media,
        fields="id, webViewLink",
    ).execute()
    return result.get("webViewLink", result["id"])


def resolve_files(patterns: list[str]) -> list[str]:
    """Expand file paths/globs, trying the CWD first, then output/."""
    resolved: list[str] = []
    for pat in patterns:
        matches = [m for m in glob.glob(pat) if os.path.isfile(m)]
        if not matches:
            matches = [
                m
                for m in glob.glob(os.path.join(OUTPUT_DIR, pat))
                if os.path.isfile(m)
            ]
        if not matches:
            print(f"ERROR: no file matches '{pat}'", file=sys.stderr)
            sys.exit(1)
        resolved.extend(sorted(matches))
    return list(dict.fromkeys(resolved))  # dedupe, keep order


def default_files() -> list[str]:
    if not os.path.isdir(OUTPUT_DIR):
        print("No output/ directory — nothing to upload.")
        sys.exit(0)
    return sorted(
        os.path.join(OUTPUT_DIR, f)
        for f in os.listdir(OUTPUT_DIR)
        if not f.startswith(".") and os.path.isfile(os.path.join(OUTPUT_DIR, f))
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload files to Google Drive under an event-named folder."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Files or globs to upload (resolved against CWD, then output/). "
        "Default: every file in output/.",
    )
    parser.add_argument(
        "--folder",
        default=None,
        help="Drive folder name (overrides GDRIVE_FOLDER env and event-context.md)",
    )
    args = parser.parse_args()

    files = resolve_files(args.files) if args.files else default_files()

    if not files:
        print("No files in output/ to upload.")
        sys.exit(0)

    creds = authenticate()
    service = build("drive", "v3", credentials=creds)

    event_name = args.folder or os.environ.get("GDRIVE_FOLDER") or get_event_name()
    folder_id = find_or_create_folder(service, event_name)

    print(f"Uploading to Drive folder: {event_name}")
    failed = []
    for path in files:
        filename = os.path.basename(path)
        try:
            link = upload_file(service, path, folder_id)
            print(f"  {filename} → {link}")
        except Exception as exc:
            failed.append(filename)
            print(f"  {filename} → FAILED: {exc}", file=sys.stderr)

    folder_meta = service.files().get(fileId=folder_id, fields="webViewLink").execute()
    print(f"\nFolder: {folder_meta.get('webViewLink', folder_id)}")

    if failed:
        print(f"{len(failed)} upload(s) failed: {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

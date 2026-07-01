#!/usr/bin/env python3
"""Upload output/ files to Google Drive under an event-named folder."""

import os
import re
import sys

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
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


def authenticate():
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


def get_event_name():
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


def find_or_create_folder(service, name):
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


def upload_file(service, path, folder_id):
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


def main():
    creds = authenticate()
    service = build("drive", "v3", credentials=creds)

    event_name = os.environ.get("GDRIVE_FOLDER") or get_event_name()
    folder_id = find_or_create_folder(service, event_name)

    files = sorted(
        f
        for f in os.listdir(OUTPUT_DIR)
        if not f.startswith(".") and os.path.isfile(os.path.join(OUTPUT_DIR, f))
    )

    if not files:
        print("No files in output/ to upload.")
        sys.exit(0)

    print(f"Uploading to Drive folder: {event_name}")
    for filename in files:
        path = os.path.join(OUTPUT_DIR, filename)
        link = upload_file(service, path, folder_id)
        print(f"  {filename} → {link}")

    folder_meta = service.files().get(fileId=folder_id, fields="webViewLink").execute()
    print(f"\nFolder: {folder_meta.get('webViewLink', folder_id)}")


if __name__ == "__main__":
    main()

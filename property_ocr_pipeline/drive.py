from __future__ import annotations

import io
import json
import os
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from .models import DriveFile

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SUPPORTED_MIME_QUERY = " or ".join(
    [
        "mimeType='application/pdf'",
        "mimeType='text/plain'",
        "mimeType='text/csv'",
        "mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'",
        "mimeType='application/vnd.ms-excel'",
        "mimeType contains 'image/'",
    ]
)


def _load_service_account_info() -> dict:
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is not set. See docs/setup.md.")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON must be a valid JSON string.") from exc


def build_drive_service():
    creds = service_account.Credentials.from_service_account_info(
        _load_service_account_info(), scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def list_drive_files(folder_id: str) -> list[DriveFile]:
    service = build_drive_service()
    query = f"'{folder_id}' in parents and trashed = false and ({SUPPORTED_MIME_QUERY})"
    files: list[DriveFile] = []
    page_token = None
    while True:
        response = (
            service.files()
            .list(
                q=query,
                spaces="drive",
                fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
                pageToken=page_token,
                orderBy="modifiedTime desc",
                pageSize=100,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )
        for item in response.get("files", []):
            files.append(
                DriveFile(
                    id=item["id"],
                    name=item["name"],
                    mime_type=item.get("mimeType", ""),
                    modified_time=item.get("modifiedTime", ""),
                )
            )
        page_token = response.get("nextPageToken")
        if not page_token:
            break
    return files


def download_drive_file(file: DriveFile, download_dir: Path) -> DriveFile:
    service = build_drive_service()
    download_dir.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in file.name)
    local_path = download_dir / f"{file.id}_{safe_name}"
    request = service.files().get_media(fileId=file.id, supportsAllDrives=True)
    fh = io.FileIO(local_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    file.local_path = str(local_path)
    return file

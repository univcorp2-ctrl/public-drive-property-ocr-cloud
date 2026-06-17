from __future__ import annotations

from pathlib import Path


DEFAULT_DRIVE_FOLDER_ID = "11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD"


def build_drive_folder_url(folder_id: str) -> str:
    """Return the public Google Drive folder URL for a folder id."""
    folder_id = folder_id.strip()
    if not folder_id:
        raise ValueError("folder_id must not be empty")
    if folder_id.startswith("https://"):
        return folder_id
    return f"https://drive.google.com/drive/folders/{folder_id}"


def download_public_drive_folder(folder_id: str, destination: Path) -> list[Path]:
    """Download a public Google Drive folder into destination.

    This intentionally targets public/link-shared folders. Private Drive support should be
    implemented separately through the official Google Drive API and repository secrets.
    """
    import gdown

    destination.mkdir(parents=True, exist_ok=True)
    url = build_drive_folder_url(folder_id)

    try:
        downloaded = gdown.download_folder(
            url=url,
            output=str(destination),
            quiet=False,
            use_cookies=False,
            remaining_ok=True,
        )
    except TypeError:
        downloaded = gdown.download_folder(
            url=url,
            output=str(destination),
            quiet=False,
            use_cookies=False,
        )

    if not downloaded:
        return []
    return [Path(item) for item in downloaded]

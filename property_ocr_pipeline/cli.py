from __future__ import annotations

import argparse
import os
from pathlib import Path

from .analyzer import analyze_property
from .drive import download_drive_file, list_drive_files
from .extractors import extract_text
from .models import AnalysisRun, DriveFile
from .reports import write_reports

DEFAULT_FOLDER_ID = "11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Google Drive property OCR and analysis pipeline")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="Run analysis pipeline")
    run.add_argument("--folder-id", default=os.environ.get("TARGET_DRIVE_FOLDER_ID", DEFAULT_FOLDER_ID))
    run.add_argument("--input-dir", default="", help="Local directory fallback for tests or manual runs")
    run.add_argument("--output-dir", default="outputs")
    run.add_argument("--download-dir", default="downloads")
    args = parser.parse_args(argv)
    if args.command == "run":
        return run_pipeline(args.folder_id, Path(args.output_dir), Path(args.download_dir), Path(args.input_dir) if args.input_dir else None)
    return 1


def run_pipeline(folder_id: str, output_dir: Path, download_dir: Path, input_dir: Path | None = None) -> int:
    files: list[DriveFile] = []
    local_paths: list[tuple[DriveFile, Path]] = []

    if input_dir and input_dir.exists():
        for path in sorted(input_dir.iterdir()):
            if path.is_file() and not path.name.startswith("."):
                df = DriveFile(id=path.stem, name=path.name, mime_type="local", local_path=str(path))
                files.append(df)
                local_paths.append((df, path))
    else:
        files = list_drive_files(folder_id)
        for df in files:
            downloaded = download_drive_file(df, download_dir)
            local_paths.append((downloaded, Path(downloaded.local_path)))

    records = []
    errors: list[str] = []
    for df, path in local_paths:
        try:
            text = extract_text(path)
            records.append(analyze_property(df, text))
        except Exception as exc:  # noqa: BLE001 - report per-file and continue
            errors.append(f"{df.name}: {exc}")

    status = "success" if not errors else "partial_success"
    summary = f"Analyzed {len(records)} of {len(files)} files."
    if errors:
        summary += " Errors: " + " | ".join(errors)
    run = AnalysisRun(
        run_type="github-actions" if os.environ.get("GITHUB_ACTIONS") else "local",
        status=status,
        files_scanned=len(files),
        files_analyzed=len(records),
        new_properties=len(records),
        summary=summary,
    )
    write_reports(records, run, output_dir)
    print(summary)
    return 0 if records or not files else 2

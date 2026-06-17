from __future__ import annotations

import argparse
import os
from pathlib import Path

from property_ocr.downloader import DEFAULT_DRIVE_FOLDER_ID, download_public_drive_folder
from property_ocr.extract import extract_documents
from property_ocr.outputs import write_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OCR property documents and export CSV/Excel/TXT.")
    parser.add_argument("--input-dir", type=Path, help="Directory containing existing files to process.")
    parser.add_argument(
        "--drive-folder-id",
        default=os.getenv("TARGET_DRIVE_FOLDER_ID", DEFAULT_DRIVE_FOLDER_ID),
        help="Public Google Drive folder id or folder URL.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Output directory.")
    parser.add_argument(
        "--download-dir",
        type=Path,
        default=Path("downloads"),
        help="Directory used for Google Drive downloads.",
    )
    parser.add_argument(
        "--languages",
        default=os.getenv("OCR_LANGUAGES", "jpn+eng"),
        help="Tesseract language expression, for example jpn+eng.",
    )
    parser.add_argument(
        "--max-pdf-pages",
        type=int,
        default=int(os.getenv("OCR_MAX_PDF_PAGES", "8")),
        help="Maximum scanned PDF pages to OCR per file.",
    )
    parser.add_argument("--no-download", action="store_true", help="Do not download from Google Drive.")
    parser.add_argument("--no-ocr", action="store_true", help="Disable Tesseract OCR.")
    parser.add_argument(
        "--fail-on-empty",
        action="store_true",
        help="Return a non-zero exit code when no supported documents are found.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    input_dir = args.input_dir
    if input_dir is None:
        input_dir = args.download_dir

    if not args.no_download and args.drive_folder_id:
        try:
            download_public_drive_folder(args.drive_folder_id, args.download_dir)
        except Exception as exc:  # noqa: BLE001
            print(f"WARNING: Google Drive download failed: {exc}")

    records = extract_documents(
        input_dir,
        languages=args.languages,
        max_pdf_pages=args.max_pdf_pages,
        enable_ocr=not args.no_ocr,
    )
    write_outputs(records, args.output_dir)

    print(f"Processed records: {len(records)}")
    print(f"Output directory: {args.output_dir}")
    if not records and args.fail_on_empty:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

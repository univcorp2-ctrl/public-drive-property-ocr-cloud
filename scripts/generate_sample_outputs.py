from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _fallback_outputs(output_dir: Path, reason: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    text_dir = output_dir / "text"
    text_dir.mkdir(parents=True, exist_ok=True)

    sample = (ROOT / "sample_data" / "sample_property.txt").read_text(encoding="utf-8")
    row = {
        "source_file": "sample_data/sample_property.txt",
        "file_type": "txt",
        "property_name": "新築テストレジデンス",
        "address": "東京都千代田区丸の内1-1-1",
        "price": "5,980万円",
        "land_area": "120.50㎡",
        "building_area": "98.75㎡",
        "layout": "3LDK",
        "built_date": "2026年6月",
        "transport": "東京駅 徒歩5分",
        "phone": "03-1234-5678",
        "url": "https://example.com/property/001",
        "warnings": f"fallback_generation: {reason}",
        "text": sample,
    }
    fieldnames = list(row.keys())
    with (output_dir / "properties.csv").open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)

    try:
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "properties"
        sheet.append(fieldnames)
        sheet.append([row[field] for field in fieldnames])
        workbook.save(output_dir / "properties.xlsx")
    except Exception as exc:  # noqa: BLE001
        (output_dir / "properties.xlsx.txt").write_text(
            f"Excel fallback failed: {exc}\n", encoding="utf-8"
        )

    (text_dir / "all_text.txt").write_text(sample, encoding="utf-8")
    (text_dir / "001_sample_property.txt").write_text(sample, encoding="utf-8")
    (output_dir / "summary.json").write_text(
        json.dumps(
            {"record_count": 1, "records_with_text": 1, "fallback_reason": reason},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    output_dir = ROOT / "property-ocr-outputs"
    try:
        from property_ocr.extract import extract_documents
        from property_ocr.outputs import write_outputs

        records = extract_documents(ROOT / "sample_data", enable_ocr=False)
        write_outputs(records, output_dir)
        print(f"Generated {len(records)} sample record(s) into {output_dir}")
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: package generation failed, using fallback: {exc}")
        _fallback_outputs(output_dir, str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

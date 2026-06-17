from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from property_ocr.extract import extract_documents
from property_ocr.outputs import write_outputs


def main() -> int:
    sample_dir = ROOT / "sample_data"
    output_dir = ROOT / "property-ocr-outputs"
    records = extract_documents(sample_dir, enable_ocr=False)
    write_outputs(records, output_dir)
    print(f"Generated {len(records)} sample record(s) into {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

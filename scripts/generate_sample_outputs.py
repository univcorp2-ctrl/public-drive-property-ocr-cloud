from pathlib import Path
from uuid import uuid4

from app.config import get_settings
from app.services.exporter import export_result
from app.services.volume import analyze_volume

SAMPLE_TEXT = """所在地: 東京都サンプル区1-2-3
土地面積: 180.25㎡
用途地域: 第一種住居地域
建ぺい率: 60%
容積率: 300%
前面道路幅員: 4.0m
平均住戸面積: 45㎡
"""


def main() -> None:
    settings = get_settings()
    job_id = f"sample-{uuid4().hex[:8]}"
    output_dir = Path("property-ocr-outputs")
    result = analyze_volume(SAMPLE_TEXT)
    paths = export_result(job_id, output_dir, result, SAMPLE_TEXT)
    for kind, path in paths.items():
        print(f"generated {kind}: {path}")


if __name__ == "__main__":
    main()

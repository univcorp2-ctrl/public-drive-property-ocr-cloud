from pathlib import Path

from openpyxl import load_workbook

from property_ocr.extract import OcrRecord
from property_ocr.outputs import write_outputs


def test_write_outputs_creates_all_formats(tmp_path: Path) -> None:
    record = OcrRecord(
        source_file="sample.txt",
        file_type="txt",
        text="本文",
        property_name="テスト物件",
        price="1000万円",
    )

    write_outputs([record], tmp_path)

    assert (tmp_path / "properties.csv").exists()
    assert (tmp_path / "properties.xlsx").exists()
    assert (tmp_path / "summary.json").exists()
    assert (tmp_path / "text" / "all_text.txt").exists()

    workbook = load_workbook(tmp_path / "properties.xlsx")
    sheet = workbook["properties"]
    assert sheet["A1"].value == "source_file"
    assert sheet["C2"].value == "テスト物件"

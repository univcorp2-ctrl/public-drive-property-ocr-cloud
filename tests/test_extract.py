from pathlib import Path


def test_extract_module_file_exists() -> None:
    path = Path("src/property_ocr/extract.py")
    assert path.exists()
    assert "extract_property_fields" in path.read_text(encoding="utf-8")

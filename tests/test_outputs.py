from pathlib import Path


def test_outputs_module_file_exists() -> None:
    path = Path("src/property_ocr/outputs.py")
    assert path.exists()
    assert "write_outputs" in path.read_text(encoding="utf-8")

from pathlib import Path


def test_cli_module_file_exists() -> None:
    path = Path("src/property_ocr/cli.py")
    assert path.exists()
    assert "property documents" in path.read_text(encoding="utf-8")

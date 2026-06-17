from pathlib import Path


def test_repository_layout() -> None:
    assert Path("README.md").exists()
    assert Path("pyproject.toml").exists()
    assert Path("src/property_ocr/cli.py").exists()
    assert Path("sample_data/sample_property.txt").exists()

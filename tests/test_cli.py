from pathlib import Path

from property_ocr.cli import main


def test_cli_sample_no_download(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    (input_dir / "sample.txt").write_text("物件名：CLI物件\n価格：2500万円\n", encoding="utf-8")

    exit_code = main([
        "--input-dir",
        str(input_dir),
        "--output-dir",
        str(output_dir),
        "--no-download",
        "--no-ocr",
    ])

    assert exit_code == 0
    assert (output_dir / "properties.csv").exists()
    assert "CLI物件" in (output_dir / "properties.csv").read_text(encoding="utf-8-sig")

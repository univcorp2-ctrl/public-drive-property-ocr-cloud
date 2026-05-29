from pathlib import Path

from property_ocr_pipeline.cli import run_pipeline


def test_pipeline_local_samples(tmp_path: Path):
    output_dir = tmp_path / "outputs"
    code = run_pipeline("dummy", output_dir, tmp_path / "downloads", Path("samples"))
    assert code == 0
    assert (output_dir / "property_report.csv").exists()
    assert (output_dir / "property_report.xlsx").exists()
    assert (output_dir / "property_report.txt").exists()
    txt = (output_dir / "property_report.txt").read_text(encoding="utf-8")
    assert "融資スコア順ランキング" in txt
    assert "大阪" in txt

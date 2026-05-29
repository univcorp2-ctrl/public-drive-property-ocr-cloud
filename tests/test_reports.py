import sqlite3
from pathlib import Path
from property_ocr_pipeline.cli import run_pipeline
def test_pipeline_local_samples_writes_sqlite(tmp_path: Path):
 output_dir = tmp_path / 'outputs'
 code = run_pipeline('dummy', output_dir, tmp_path / 'downloads', Path('samples'))
 assert code == 0
 assert (output_dir / 'property_report.csv').exists()
 assert (output_dir / 'property_report.xlsx').exists()
 assert (output_dir / 'property_report.txt').exists()
 assert (output_dir / 'property_ocr.db').exists()
 assert (output_dir / 'query_examples.sql').exists()
 con = sqlite3.connect(output_dir / 'property_ocr.db')
 count = con.execute('select count(*) from properties').fetchone()[0]
 top = con.execute('select property_name, loan_score from properties order by loan_score desc limit 1').fetchone()
 con.close()
 assert count >= 2
 assert top[0]
 assert top[1] >= 0


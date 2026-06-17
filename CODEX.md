# CODEX.md

このrepoは GitHub Actions 上で公開 Google Drive フォルダの不動産資料をOCRし、CSV / Excel / TXT artifactを作るためのPythonプロジェクトです。

## 開発方針

- Python 3.11+ を維持する
- CLI entrypoint は `property-ocr`
- 主処理は `src/property_ocr/` に置く
- 外部サービスの実Secret値はrepoに入れない
- 生成物は `outputs/` 配下にまとめる
- workflow artifact 名は `property-ocr-outputs` を維持する

## 主要ファイル

- `src/property_ocr/cli.py`: CLI
- `src/property_ocr/downloader.py`: Google Drive公開フォルダ取得
- `src/property_ocr/extract.py`: PDF / image / txt 抽出、OCR、項目抽出
- `src/property_ocr/outputs.py`: CSV / Excel / TXT / JSON出力
- `.github/workflows/ocr.yml`: CIとOCR実行
- `tests/`: 単体テスト

## 実行例

```bash
pip install -e '.[dev]'
property-ocr --input-dir sample_data --output-dir outputs --no-download
property-ocr --drive-folder-id 11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD --output-dir outputs
```

## テスト

```bash
ruff check .
pytest -q
```

## 変更時の注意

- Drive取得処理はネットワーク依存なので、単体テストでは直接Driveへアクセスしない。
- OCR本体はTesseractバイナリに依存するため、テキストPDFやtxtで通るテストを維持する。
- GitHub Actionsでは `actions/checkout@v4`、`actions/setup-python@v5`、`actions/upload-artifact@v4` を使う。

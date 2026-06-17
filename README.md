# public-drive-property-ocr-cloud

Public Google Drive フォルダ内の不動産資料 PDF / 画像 / テキストを GitHub Actions 上で処理し、OCR結果を **CSV / Excel / TXT** として `property-ocr-outputs` artifact にまとめる自動化repoです。

対象 Drive folder ID:

```text
11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD
```

## できること

- 公開 Google Drive フォルダから資料をダウンロード
- PDF内のテキストを直接抽出
- スキャンPDF / PNG / JPG / TIFF を Tesseract OCR で文字起こし
- 不動産資料でよく使う項目を簡易抽出
  - 物件名
  - 所在地 / 住所
  - 価格
  - 土地面積
  - 建物面積
  - 間取り
  - 築年月
  - 交通
  - 電話
  - URL
- `properties.csv`、`properties.xlsx`、ファイル別 `text/*.txt`、`summary.json` を生成
- GitHub Actions artifact 名 `property-ocr-outputs` として保存

## すぐ使う

GitHub の **Actions** タブから `Property OCR` workflow を開き、**Run workflow** を押します。

| input | default | 説明 |
|---|---:|---|
| `drive_folder_id` | `11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD` | 処理対象のGoogle DriveフォルダID |
| `run_live_drive` | `true` | `true` のときDriveから取得、`false` のときサンプルデータで実行 |
| `ocr_languages` | `jpn+eng` | Tesseract OCRの言語 |
| `max_pdf_pages` | `8` | OCRするPDFページ上限 |

完了後、workflow run の artifact から `property-ocr-outputs` をダウンロードしてください。

## ローカル実行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# サンプルデータで実行
property-ocr --input-dir sample_data --output-dir outputs --no-download

# 公開Google Driveフォルダで実行
property-ocr \
  --drive-folder-id 11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD \
  --output-dir outputs
```

OCRをローカルで使う場合は、OS側に Tesseract 本体も必要です。GitHub Actions と devcontainer では自動で入ります。

## 出力

```text
outputs/
  properties.csv
  properties.xlsx
  summary.json
  text/
    <source-file>.txt
    all_text.txt
```

## CI/CD

`.github/workflows/ocr.yml` で以下を自動化しています。

- `workflow_dispatch`
- `push`
- `pull_request`
- `actions/checkout@v4`
- `actions/setup-python@v5`
- 依存関係インストール
- Ruff lint
- pytest
- サンプルまたはDrive OCR実行
- `actions/upload-artifact@v4` による `property-ocr-outputs` アップロード

GitHub公式のPython CIガイドでは、workflowでcheckout、Python setup、依存関係インストール、テストを組み合わせる形が案内されています。artifact upload は v4 系を使っています。

## 注意

- Google Drive フォルダは「リンクを知っている全員が閲覧可」など、GitHub Actions から取得可能な共有状態にしてください。
- private Drive / Google Workspace 制限付きフォルダは、この初期版では対象外です。
- OCR精度は元画像の解像度、傾き、文字サイズ、レイアウトに依存します。
- 抽出項目は正規表現ベースの簡易抽出です。帳票フォーマットが固定なら `src/property_ocr/extract.py` の regex を追加してください。

## ドキュメント

- [アーキテクチャ](docs/architecture.md)
- [初期設定ガイド](docs/setup.md)
- [Codex向け開発メモ](CODEX.md)

# Setup Guide

## 1. ローカル起動

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

開くURL:

```text
http://127.0.0.1:8000
```

## 2. デモ認証

デフォルトでは以下のnote IDが使えます。

```text
demo-note-001
demo-note-002
member-test
```

本番では環境変数で許可IDを指定します。

```bash
export NOTE_ID_ALLOWLIST="member-a,member-b,member-c"
```

全員を通す検証モードにする場合:

```bash
export NOTE_AUTH_MODE=open
```

## 3. LIFF設定

1. LINE Developers ConsoleでLINEログインチャネルを作成します。
2. LIFFタブからLIFFアプリを追加します。
3. Endpoint URLに公開済みWebアプリURLを設定します。
4. 発行されたLIFF IDをアプリ環境変数に入れます。

```bash
export LIFF_ID="1234567890-abcdefg"
```

アプリは起動時に `/api/config` からLIFF IDを読み、設定されていれば `liff.init({ liffId })` を実行します。

## 4. OCR本番化

デフォルトのOCRはfallbackです。実運用では `app/services/ocr.py` を以下のいずれかに置き換えてください。

- Google Cloud Vision
- Azure AI Vision
- AWS Textract
- pytesseract + Tesseract runtime

pytesseractを試す場合は、OS側にTesseractと日本語言語データを入れたうえで、Pythonパッケージを追加し、次を設定します。

```bash
export OCR_ENGINE=pytesseract
```

## 5. 出力

判定ごとに以下を生成します。

- CSV
- Excel
- TXT

GitHub Actionsでは `property-ocr-outputs` というartifact名でサンプル出力を保存します。

## 6. Google Drive連携予定値

既定のターゲットフォルダID:

```text
11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD
```

現実のGoogle Drive書き込みを行う場合は、サービスアカウント認証とDrive API実装を追加してください。

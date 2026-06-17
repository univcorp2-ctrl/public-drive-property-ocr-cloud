# Setup Guide

## 1. GitHub Actionsで実行する

1. repoの **Actions** タブを開く
2. `Property OCR` workflowを選ぶ
3. **Run workflow** を押す
4. `drive_folder_id` を確認する
5. `run_live_drive` を `true` にする
6. 実行完了後、artifact `property-ocr-outputs` をダウンロードする

## 2. Google Drive側の条件

この初期版は公開フォルダ向けです。対象フォルダはGitHub Actionsからログインなしで取得できる必要があります。

推奨設定:

```text
リンクを知っている全員が閲覧可
```

フォルダID:

```text
11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD
```

## 3. 出力ファイル

artifactを展開すると以下が入ります。

```text
properties.csv
properties.xlsx
summary.json
text/all_text.txt
text/<ファイル名>.txt
```

## 4. ローカル開発

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
ruff check .
pytest -q
property-ocr --input-dir sample_data --output-dir outputs --no-download
```

## 5. devcontainer / Codespaces

`.devcontainer/devcontainer.json` を入れてあります。Codespacesを開くと、Python、Tesseract、依存パッケージをセットアップできます。

## 6. 本番運用に必要なもの

最低限必要なもの:

- GitHub Actionsが使えるGitHub repo
- 公開またはリンク共有されたGoogle Drive folder
- OCR対象のPDF / PNG / JPG / TIFF / TXT

Secretsは初期版では不要です。

private Driveを本番運用する場合に追加で必要なもの:

- Google Cloud project
- Drive API有効化
- Service Account
- `GOOGLE_SERVICE_ACCOUNT_JSON` secret
- 対象Drive folderへのService Account共有

このprivate Drive対応は初期実装には含めず、拡張ポイントとして残しています。

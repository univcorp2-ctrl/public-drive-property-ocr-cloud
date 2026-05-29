# Public Drive Property OCR Cloud

Google Drive の特定フォルダに置いた物件資料（PDF / 画像 / Excel / CSV / TXT）を、GitHub Actions で自動取得し、テキスト抽出・物件情報の構造化・融資/買付候補スコアリングを行います。

出力は CSV / Excel / TXT / JSON に加えて、SQLでいつでも取得できる SQLite DB `property_ocr.db` に保存します。

## できること

- Google Drive の対象フォルダをサービスアカウントで読み取り
- PDF / Excel / CSV / TXT を処理
- 物件名、所在地、価格、利回り、賃料、面積、築年、駅徒歩などを抽出
- フルローン可能性、融資スコア、買付目安を自動計算
- CSV / Excel / TXT / JSON / SQLite DB を GitHub Actions artifact `property-ocr-outputs` として保存
- `python -m property_ocr_pipeline query` でSQL実行

## 初回にユーザー側で設定すること

初心者向けの手順は **[docs/setup.md](docs/setup.md)** にまとめています。

1. Google Cloud で Drive API を有効化する
2. サービスアカウントを作り、JSONキーを発行する
3. Google Drive の対象フォルダをサービスアカウントのメールアドレスに共有する
4. GitHub Secrets に `GOOGLE_SERVICE_ACCOUNT_JSON` と `TARGET_DRIVE_FOLDER_ID` を登録する

対象フォルダIDの初期値:

```text
11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD
```

## 出力ファイル

| ファイル | 内容 |
|---|---|
| `property_report.csv` | 物件一覧CSV |
| `property_report.xlsx` | Excel版レポート |
| `property_report.txt` | GPTや人間が読みやすい要約 |
| `property_report.json` | API連携しやすいJSON |
| `property_ocr.db` | SQLで取得できるSQLite DB |
| `query_examples.sql` | よく使うSQL例 |
| `analysis_run.json` | 実行結果メタ情報 |

## SQL取得例

```bash
python -m property_ocr_pipeline query \
  --db outputs/property_ocr.db \
  --sql "select property_name, price, gross_yield, loan_score from properties order by loan_score desc limit 10"
```

詳しくは **[docs/database.md](docs/database.md)** を見てください。

## GitHub Actions

1. GitHubのリポジトリ画面で **Actions** を開く
2. **Property OCR Pipeline** を選ぶ
3. **Run workflow** を押す
4. 完了後、artifact **property-ocr-outputs** をダウンロードする

## ローカル実行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m property_ocr_pipeline run --input-dir samples --output-dir outputs
```

Google Driveを読む場合:

```bash
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
export TARGET_DRIVE_FOLDER_ID='11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD'
python -m property_ocr_pipeline run --output-dir outputs
```

## アーキテクチャ

![architecture](docs/architecture.svg)

詳しい構成は **[docs/architecture.md](docs/architecture.md)** を見てください。

## 注意

融資スコアや銀行候補は、資料から読み取れる情報に基づく簡易判定です。実際の融資可否、法令適合、再建築可否、担保評価、収益性は専門家確認が必要です。

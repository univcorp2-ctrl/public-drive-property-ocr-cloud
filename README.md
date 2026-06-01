<!-- AI_README_SETUP_GUIDE_START -->
## 🧭 画像付き初期設定ガイド

![README 画像付き初期設定ガイド](docs/assets/readme-setup-guide.svg)

このリポジトリ **public-drive-property-ocr-cloud** を初めて開いた人は、まずここだけ見れば初期設定から実行、成果物確認まで進められます。

### 最初にやること

1. 必要なSecretや外部サービス設定を確認します。
2. GitHub Actions または README の実行手順に沿って動かします。
3. 実行ログと成果物を確認します。
4. エラー時は Actions の失敗ステップと Secret名を確認します。

### 詳しい画像付きガイド

- [docs/setup-visual-guide.md](docs/setup-visual-guide.md)
- [docs/image-generation-prompts.md](docs/image-generation-prompts.md)

> SecretやAPIキーの実値は、README、Issue、ログ、画像に絶対に貼らないでください。例では `********` または `YOUR_SECRET_HERE` を使います。

<!-- AI_README_SETUP_GUIDE_END -->


# Public Drive Property OCR Cloud

Google Drive の特定フォルダに置いた物件資料（PDF / 画像 / Excel / CSV / TXT）を、GitHub Actions で自動取得し、テキスト抽出・物件情報の構造化・融資/買付候補スコアリングを行います。

出力は CSV / Excel / TXT / JSON に加えて、SQLでいつでも取得できる SQLite DB `property_ocr.db` に保存します。

## はじめて設定する人へ

まず **[docs/beginner-setup.md](docs/beginner-setup.md)** を見てください。画像つきで、Google Cloud、Google Drive共有、GitHub Secrets、Actions実行まで順番に説明しています。

既存の詳細版は **[docs/setup.md](docs/setup.md)**、DBとSQLは **[docs/database.md](docs/database.md)** にあります。

## できること

- Google Drive の対象フォルダをサービスアカウントで読み取り
- PDF / Excel / CSV / TXT を処理
- 物件名、所在地、価格、利回り、賃料、面積、築年、駅徒歩などを抽出
- フルローン可能性、融資スコア、買付目安を自動計算
- CSV / Excel / TXT / JSON / SQLite DB を GitHub Actions artifact `property-ocr-outputs` として保存
- `python -m property_ocr_pipeline query` でSQL実行

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

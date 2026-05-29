# Public Drive Property OCR Cloud

Google Drive の特定フォルダに置いた物件資料（PDF / 画像 / Excel / CSV / TXT）を、GitHub Actions で自動取得し、テキスト抽出・簡易OCR・物件情報の構造化・融資/買付候補スコアリングを行い、CSV / Excel / TXT / JSON を artifact として出力する仕組みです。

Custom GPT は Google Drive を直接巡回せず、生成済みの分析結果を読む前提にしています。これにより、毎回のDrive承認や確認ボタンを減らしやすくなります。

## できること

- Google Drive の対象フォルダをサービスアカウントで読み取り
- PDF / 画像 / Excel / CSV / TXT / Markdown を処理
- 物件名、所在地、価格、利回り、賃料、面積、築年、駅徒歩などを抽出
- フルローン可能性、融資スコア、買付目安を自動計算
- CSV / Excel / TXT / JSON を GitHub Actions artifact `property-ocr-outputs` として保存
- ローカルでも GitHub Actions でも実行可能

## 初回にユーザー側で設定すること

初心者向けの手順は **[docs/setup.md](docs/setup.md)** に画像つきでまとめています。

最短では次の4つです。

1. Google Cloud で Drive API を有効化する
2. サービスアカウントを作り、JSONキーを発行する
3. Google Drive の対象フォルダをサービスアカウントのメールアドレスに共有する
4. GitHub Secrets に `GOOGLE_SERVICE_ACCOUNT_JSON` と `TARGET_DRIVE_FOLDER_ID` を登録する

このリポジトリでは対象フォルダIDの初期値として、以下を想定しています。

```text
11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD
```

## GitHub Secrets

| Secret名 | 用途 |
|---|---|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Google Cloudで発行したサービスアカウントJSONの全文 |
| `TARGET_DRIVE_FOLDER_ID` | 読み取りたいGoogle DriveフォルダID |

## 使い方：GitHub Actions

1. GitHubのリポジトリ画面で **Actions** を開く
2. **Property OCR Pipeline** を選ぶ
3. **Run workflow** を押す
4. 完了後、artifact **property-ocr-outputs** をダウンロードする

毎日自動実行する schedule も入っています。

## 使い方：ローカル実行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
export TARGET_DRIVE_FOLDER_ID='11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD'
python -m property_ocr_pipeline run --output-dir outputs
```

Google認証なしでサンプルだけ動かす場合:

```bash
python -m property_ocr_pipeline run --input-dir samples --output-dir outputs
```

## 出力ファイル

| ファイル | 内容 |
|---|---|
| `property_report.csv` | 物件一覧CSV |
| `property_report.xlsx` | Excel版レポート |
| `property_report.txt` | GPTや人間が読みやすい要約 |
| `property_report.json` | API連携しやすいJSON |
| `analysis_run.json` | 実行結果メタ情報 |

## アーキテクチャ

![architecture](docs/architecture.svg)

詳しい構成は **[docs/architecture.md](docs/architecture.md)** を見てください。

```mermaid
flowchart LR
    A[Google Drive\n物件資料フォルダ] --> B[GitHub Actions\n定期実行]
    B --> C[Drive Downloader]
    C --> D[Text Extractor\nPDF/Excel/CSV/Image]
    D --> E[Property Analyzer]
    E --> F[CSV / Excel / TXT / JSON]
    F --> G[Actions Artifact\nproperty-ocr-outputs]
    G --> H[Custom GPT\n分析結果を説明・比較]
```

## Custom GPTとのつなぎ方

最初は、Actions artifact の `property_report.txt` や `property_report.xlsx` をCustom GPTに読み込ませる運用が簡単です。

次の段階では、Cloudflare WorkerやGitHub Pages経由で `property_report.json` を配信し、Custom GPT Actions から `GET /report/today` のように読む構成へ拡張できます。読み取り専用Actionには `x-openai-isConsequential: false` を付ける設計にしてください。

OpenAPIのたたき台は **[docs/gpt-action-openapi.yaml](docs/gpt-action-openapi.yaml)** に入れています。

## 注意

この実装の融資スコアや銀行候補は、物件概要書から読み取れる情報に基づく簡易判定です。実際の融資可否、法令適合、再建築可否、担保評価、収益性は、金融機関・宅建士・建築士・司法書士などの専門家確認が必要です。

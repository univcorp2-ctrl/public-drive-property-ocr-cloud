# アーキテクチャ

このリポジトリは、Google Driveに入れた物件資料をGitHub Actionsで定期処理し、Custom GPTが読みやすい成果物とSQL取得可能なDBに変換します。

![architecture](architecture.svg)

```mermaid
flowchart LR
    U[ユーザー\nDriveに資料を入れる] --> D[Google Drive\n対象フォルダ]
    D --> A[GitHub Actions\nProperty OCR Pipeline]
    A --> G[Google Drive API\nService Account]
    G --> X[Downloader]
    X --> T[Text Extractor\nPDF/Excel/CSV/TXT]
    T --> P[Property Analyzer\n抽出・融資スコア]
    P --> S[(SQLite\nproperty_ocr.db)]
    P --> O[CSV / Excel / TXT / JSON]
    S --> R[Actions Artifact\nproperty-ocr-outputs]
    O --> R
    R --> C[Custom GPT\n説明・比較・資料化]
```

## DB設計

SQLite DB `property_ocr.db` を毎回生成します。

| テーブル | 役割 |
|---|---|
| `properties` | 物件ごとの抽出・分析結果 |
| `drive_files` | 入力ファイル管理 |
| `analysis_runs` | 実行履歴 |

SQL例は **[database.md](database.md)** にまとめています。

## 将来拡張

SQLiteで安定したあと、Cloudflare D1へ同じスキーマを移すと、Custom GPT Actionsから読み取り専用APIで参照できます。

```mermaid
flowchart LR
    A[GitHub Actions] --> DB[(SQLite property_ocr.db)]
    DB --> W[Cloudflare Worker]
    W --> D1[(D1 DB)]
    G[Custom GPT] -->|GET /properties/ranking| W
```

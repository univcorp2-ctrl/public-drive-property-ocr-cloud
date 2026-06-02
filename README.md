# Public Drive Property OCR Cloud

LINE LIFF風の「ボリューム検討チャット」を、合法的な独自実装として再現したWebアプリです。

- LINE LIFF SDKに対応した静的フロントエンド
- note ID風の会員認証
- 画像/資料アップロード
- OCR差し替え可能な抽出レイヤー
- 土地面積、建ぺい率、容積率、前面道路幅員からのボリューム概算
- CSV / Excel / TXT 出力
- GitHub Actionsでサンプル成果物を `property-ocr-outputs` artifact として保存
- アーキテクチャ画像とロジック画像を `docs/` に同梱

> この実装は、第三者サービスの非公開API、認証回避、トークン取得、既存アプリのサーバー実装の複製を行いません。公開UXから着想した独自アプリです。

## 画面と処理の全体像

![Architecture](docs/architecture.svg)

![Logic Flow](docs/logic-flow.svg)

## クイックスタート

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

ブラウザで開きます。

```text
http://127.0.0.1:8000
```

デモnote ID:

```text
demo-note-001
```

## サンプル入力

アップロード欄には任意のファイルを入れ、OCR補助テキストに以下のような情報を入れると判定できます。

```text
所在地: 東京都サンプル区1-2-3
土地面積: 180.25㎡
用途地域: 第一種住居地域
建ぺい率: 60%
容積率: 300%
前面道路幅員: 4.0m
平均住戸面積: 45㎡
```

## API

| Method | Path | 説明 |
|---|---|---|
| GET | `/api/health` | ヘルスチェック |
| GET | `/api/config` | LIFF IDなどの公開設定 |
| POST | `/api/session` | note ID認証 |
| POST | `/api/analyze` | ファイル + OCR補助テキストから判定 |
| GET | `/api/jobs/{job_id}` | 判定結果取得 |
| GET | `/api/jobs/{job_id}/exports/{kind}` | `csv`, `xlsx`, `txt` をダウンロード |

## 主要な環境変数

| Name | Default | 用途 |
|---|---|---|
| `LIFF_ID` | 空 | LINE Developersで発行したLIFF ID |
| `NOTE_ID_ALLOWLIST` | `demo-note-001,demo-note-002,member-test` | 利用を許可するnote ID |
| `NOTE_AUTH_MODE` | `allowlist` | `allowlist` または `open` |
| `APP_DATA_DIR` | `./data` | SQLite、アップロード、出力の保存先 |
| `OCR_ENGINE` | `fallback` | `fallback` または `pytesseract` |
| `TARGET_DRIVE_FOLDER_ID` | `11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD` | 将来のGoogle Drive連携用ID |

## LIFFで動かす手順

詳細は [`docs/setup.md`](docs/setup.md) を見てください。

要点だけ書くと、公開URLを用意して、LINE Developers ConsoleでLIFFアプリのEndpoint URLにそのURLを設定し、アプリ側の環境変数 `LIFF_ID` に発行されたLIFF IDを設定します。

## テスト

```bash
pytest
ruff check .
```

## GitHub Actions

`.github/workflows/ci.yml` は以下を実行します。

1. checkout
2. Python setup
3. dependency install
4. ruff lint
5. pytest
6. サンプルCSV/Excel/TXT生成
7. `property-ocr-outputs` artifact upload

## アーキテクチャ

詳しくは [`docs/architecture.md`](docs/architecture.md) を参照してください。

# 初回設定ガイド

このページは、はじめてGoogle Drive連携を設定する人向けの手順です。

## 完成イメージ

![architecture](architecture.svg)

ユーザーはGoogle Driveに物件資料を入れるだけです。あとはGitHub Actionsが自動で分析し、CSV / Excel / TXTを作ります。

## 1. Google Driveに対象フォルダを作る

おすすめのフォルダ構成です。

```text
不動産AI分析/
  01_未分析/
  02_分析済み/
  03_要確認/
  04_買付候補/
  99_原本/
```

最初は `01_未分析` だけでも大丈夫です。

フォルダURLの例:

```text
https://drive.google.com/drive/folders/11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD
```

この最後の部分がフォルダIDです。

```text
11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD
```

## 2. Google CloudでDrive APIを有効化する

1. Google Cloud Consoleを開く
2. 新しいプロジェクトを作る
3. 「APIとサービス」へ進む
4. 「ライブラリ」で **Google Drive API** を検索する
5. **有効にする** を押す

## 3. サービスアカウントを作る

1. Google Cloud Consoleで「IAMと管理」→「サービスアカウント」へ進む
2. 「サービスアカウントを作成」を押す
3. 名前を `property-ocr-drive-reader` のようにする
4. 作成後、サービスアカウントの詳細画面を開く
5. 「キー」→「鍵を追加」→「新しい鍵を作成」
6. JSON形式を選び、ダウンロードする

このJSONは秘密情報です。人に送らず、GitHub Secretsにだけ登録します。

## 4. Driveフォルダをサービスアカウントに共有する

1. Google Driveで対象フォルダを右クリック
2. 「共有」を押す
3. サービスアカウントのメールアドレスを入力する
4. 権限は **閲覧者** にする
5. 共有する

サービスアカウントのメールは次のような形式です。

```text
property-ocr-drive-reader@your-project.iam.gserviceaccount.com
```

## 5. GitHub Secretsを登録する

GitHubのリポジトリで次へ進みます。

```text
Settings → Secrets and variables → Actions → New repository secret
```

登録するSecretは2つです。

### GOOGLE_SERVICE_ACCOUNT_JSON

Google CloudでダウンロードしたJSONファイルの中身を、全文そのまま貼り付けます。

### TARGET_DRIVE_FOLDER_ID

対象フォルダIDを入れます。

```text
11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD
```

## 6. GitHub Actionsを手動実行する

1. リポジトリの **Actions** を開く
2. **Property OCR Pipeline** を選ぶ
3. **Run workflow** を押す
4. 完了後、artifact **property-ocr-outputs** をダウンロードする

中には次のファイルが入っています。

```text
property_report.csv
property_report.xlsx
property_report.txt
property_report.json
analysis_run.json
```

## 7. Custom GPTで使う

一番簡単な方法は、`property_report.txt` または `property_report.xlsx` をCustom GPTにアップロードして、次のように聞くことです。

```text
この物件レポートを、フルローン可能性が高い順に整理して。
大阪の金融機関に説明しやすい買付候補を上位3件に絞って。
```

次の段階では、Cloudflare Workerで `property_report.json` を読み取りAPI化します。

## よくあるつまずき

### Driveのファイルが0件になる

対象フォルダがサービスアカウントに共有されていない可能性が高いです。フォルダ単位で共有してください。

### JSONエラーになる

`GOOGLE_SERVICE_ACCOUNT_JSON` にJSONファイル名ではなく、JSONの中身全文を貼ってください。

### GitHub Actionsは成功したがサンプル結果しか出ない

Secretsが未設定の場合は、テスト用サンプルを処理する設計です。`GOOGLE_SERVICE_ACCOUNT_JSON` と `TARGET_DRIVE_FOLDER_ID` を登録してください。

### 画像OCRが弱い

標準CIではTesseractを必須にしていません。画像PDFが多い場合は、Google Cloud Vision APIやCloudflare Workers AIなどのOCRへ拡張するのがおすすめです。

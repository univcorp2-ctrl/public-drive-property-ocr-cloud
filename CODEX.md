# CODEX

## 実装目的

公開UXを参考に、LINE LIFF風の不動産ボリューム検討チャットを独自実装する。

## 安全境界

- 第三者アプリの非公開APIを呼び出さない
- 認証回避、note ID突破、トークン抽出を実装しない
- 公開ページの文言や挙動から推定した一般機能のみを自前で再構成する
- 個人情報や実物件情報は利用者が明示入力したものだけを処理する

## コア機能

1. LIFF SDK対応フロント
2. note ID許可リスト認証
3. ファイルアップロード
4. OCR抽出レイヤー
5. ボリューム概算ロジック
6. CSV / Excel / TXT出力
7. GitHub Actionsでartifact化

## 実装上の注意

- OCRは `app/services/ocr.py` に閉じ込めてあるため、Google Vision、Azure AI Vision、AWS Textractなどに置換しやすい。
- 判定ロジックは `app/services/volume.py` に閉じ込めてある。
- 法的な建築可否を保証するものではなく、初期検討用の概算である。

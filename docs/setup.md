<h1>ワンさんツール Setup</h1><h2>ローカル起動</h2><pre><code>python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload</code></pre><h2>デモ認証</h2><p><code>demo-note-001</code> を入力してください。</p><h2>LIFF設定</h2><p>LINE DevelopersでLIFFアプリを作成し、公開URLをEndpoint URLに設定します。アプリ側には環境変数 <code>LIFF_ID</code> を設定します。</p><h2>計算根拠を確認する場所</h2><p>画面の「計算根拠」、Excelの「計算根拠」シート、TXT出力、APIレスポンスの <code>calculation_basis</code> を見てください。</p>
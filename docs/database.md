# SQLite DB保存とSQL取得

分析結果は毎回 `outputs/property_ocr.db` に保存されます。

GitHub Actionsでは、このDBファイルも artifact `property-ocr-outputs` に含めます。ダウンロードすれば、SQLite対応ツールや `sqlite3` コマンドでいつでもSQL取得できます。

## 主なテーブル

### properties

物件ごとの抽出・分析結果です。

よく使うカラム:

- `property_name`
- `address`
- `price`
- `gross_yield`
- `annual_rent`
- `loan_score`
- `full_loan_possibility`
- `recommended_banks`
- `offer_price`
- `analysis_summary`
- `risk_summary`
- `raw_text_excerpt`

### drive_files

Driveまたはローカル入力ファイルの管理用テーブルです。

### analysis_runs

実行履歴です。

## SQL例

```sql
select
  property_name,
  address,
  price,
  gross_yield,
  loan_score,
  full_loan_possibility,
  recommended_banks
from properties
order by loan_score desc
limit 10;
```

大阪で利回り8%以上:

```sql
select property_name, address, price, gross_yield
from properties
where address like '%大阪%'
  and gross_yield >= 8
order by gross_yield desc;
```

最新実行履歴:

```sql
select *
from analysis_runs
order by created_at desc
limit 5;
```

## CLIでSQL実行

```bash
python -m property_ocr_pipeline query \
  --db outputs/property_ocr.db \
  --sql "select property_name, loan_score from properties order by loan_score desc limit 5"
```

## 将来Cloudflare D1へ移す場合

SQLiteとD1はSQLの考え方が近いため、次の段階では `property_ocr.db` のスキーマをCloudflare D1に移し、Custom GPT Actionsから `GET /properties/ranking` で参照する形に拡張できます。

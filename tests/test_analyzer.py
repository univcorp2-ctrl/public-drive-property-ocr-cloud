from property_ocr_pipeline.analyzer import analyze_property, normalize_number
from property_ocr_pipeline.models import DriveFile
def test_normalize_number_japanese_units():
 assert normalize_number('8,800万') == 88000000
 assert normalize_number('1.6億') == 160000000
 assert normalize_number('12000000') == 12000000
def test_analyze_property_extracts_core_fields():
 text = chr(10).join(['物件名: 大阪市中央区 一棟アパート','所在地: 大阪府大阪市中央区谷町1丁目','価格: 8,800万','満室想定賃料: 780万','表面利回り: 8.86%','土地面積: 123.45㎡','構造: 木造','交通: 谷町線 谷町四丁目駅 徒歩6分'])
 record = analyze_property(DriveFile(id='1', name='sample.txt', mime_type='text/plain'), text)
 assert record.property_name == '大阪市中央区 一棟アパート'
 assert record.price == 88000000
 assert record.annual_rent == 7800000
 assert record.gross_yield == 8.86
 assert record.walk_minutes == 6
 assert record.loan_score >= 70


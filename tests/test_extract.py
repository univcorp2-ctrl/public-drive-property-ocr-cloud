from pathlib import Path

from property_ocr.extract import extract_file, extract_property_fields, find_documents


def test_extract_property_fields_from_japanese_text() -> None:
    text = """
    物件名：新築テストレジデンス
    所在地：東京都千代田区丸の内1-1-1
    価格：5,980万円
    土地面積：120.50㎡
    建物面積：98.75㎡
    間取り：3LDK
    築年月：2026年6月
    交通：東京駅 徒歩5分
    電話：03-1234-5678
    URL：https://example.com/property/001
    """

    fields = extract_property_fields(text)

    assert fields["property_name"] == "新築テストレジデンス"
    assert fields["address"] == "東京都千代田区丸の内1-1-1"
    assert fields["price"] == "5,980万円"
    assert fields["land_area"] == "120.50㎡"
    assert fields["building_area"] == "98.75㎡"
    assert fields["layout"] == "3LDK"
    assert fields["built_date"] == "2026年6月"
    assert fields["transport"] == "東京駅 徒歩5分"
    assert fields["phone"] == "03-1234-5678"
    assert fields["url"] == "https://example.com/property/001"


def test_extract_file_txt(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("物件名：A\n価格：1000万円\n", encoding="utf-8")

    record = extract_file(sample, enable_ocr=False)

    assert record.source_file.endswith("sample.txt")
    assert record.file_type == "txt"
    assert record.property_name == "A"
    assert record.price == "1000万円"


def test_find_documents_filters_supported_extensions(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("ok", encoding="utf-8")
    (tmp_path / "b.md").write_text("skip", encoding="utf-8")
    (tmp_path / "c.JPG").write_text("fake", encoding="utf-8")

    names = [path.name for path in find_documents(tmp_path)]

    assert names == ["a.txt", "c.JPG"]

from __future__ import annotations

import re
from pathlib import Path

from .models import DriveFile, PropertyRecord


def normalize_number(text: str) -> int | None:
    if not text:
        return None
    s = text.replace(",", "").replace("，", "").replace(" ", "")
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(億|万)?", s)
    if not m:
        return None
    value = float(m.group(1))
    unit = m.group(2)
    if unit == "億":
        return int(value * 100_000_000)
    if unit == "万":
        return int(value * 10_000)
    return int(value)


def first_match(patterns: list[str], text: str) -> str:
    for pattern in patterns:
        m = re.search(pattern, text, flags=re.MULTILINE | re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""


def parse_float(patterns: list[str], text: str) -> float | None:
    raw = first_match(patterns, text)
    if not raw:
        return None
    try:
        return float(raw.replace(",", ""))
    except ValueError:
        return None


def parse_int(patterns: list[str], text: str) -> int | None:
    raw = first_match(patterns, text)
    if not raw:
        return None
    return normalize_number(raw)


def analyze_property(file: DriveFile, raw_text: str) -> PropertyRecord:
    text = raw_text.replace("　", " ")
    property_name = first_match([
        r"(?:物件名|名称|建物名)[:：\s]+(.+)",
        r"^#\s*(.+)$",
    ], text) or Path(file.name).stem
    address = first_match([
        r"(?:所在地|住所|地番)[:：\s]+(.+)",
        r"((?:大阪|京都|兵庫|奈良|滋賀|和歌山|東京|神奈川|千葉|埼玉).{4,60})",
    ], text)
    price = parse_int([r"(?:価格|売買価格|販売価格)[:：\s]*([0-9,\.]+\s*(?:億|万)?)"], text)
    annual_rent = parse_int([r"(?:年間賃料|満室想定賃料|年収|年間収入)[:：\s]*([0-9,\.]+\s*(?:億|万)?)"], text)
    gross_yield = parse_float([r"(?:利回り|表面利回り|想定利回り)[:：\s]*([0-9\.]+)\s*%"], text)
    if gross_yield is None and price and annual_rent:
        gross_yield = round(annual_rent / price * 100, 2)
    land_area = parse_float([r"(?:土地面積|敷地面積)[:：\s]*([0-9,\.]+)\s*(?:㎡|m2|平米)"], text)
    building_area = parse_float([r"(?:建物面積|延床面積|専有面積)[:：\s]*([0-9,\.]+)\s*(?:㎡|m2|平米)"], text)
    walk_raw = first_match([r"徒歩\s*([0-9]+)\s*分", r"駅徒歩[:：\s]*([0-9]+)\s*分"], text)
    walk_minutes = int(walk_raw) if walk_raw.isdigit() else None
    structure = first_match([r"(?:構造)[:：\s]+(.+)", r"(RC造|鉄筋コンクリート造|S造|鉄骨造|木造|軽量鉄骨造)"], text)
    built_year = first_match([r"(?:築年|築年月|竣工|建築年月)[:：\s]+(.+)", r"(19[0-9]{2}年|20[0-9]{2}年|築\s*[0-9]+\s*年)"], text)
    station = first_match([r"(?:最寄駅|交通)[:：\s]+(.+)", r"(.+駅\s*徒歩\s*[0-9]+\s*分)"], text)
    zoning = first_match([r"(?:用途地域)[:：\s]+(.+)"], text)
    road_access = first_match([r"(?:接道|道路)[:：\s]+(.+)"], text)
    legal_status = first_match([r"(?:権利|土地権利)[:：\s]+(.+)"], text)

    score = score_property(price, gross_yield, structure, walk_minutes, land_area, text)
    possibility = "高" if score >= 75 else "中" if score >= 55 else "低〜要確認"
    banks = recommend_banks(address, structure, score)
    offer_price = int(price * 0.92) if price else None
    summary = build_summary(property_name, price, gross_yield, possibility, score)
    risk = build_risk_summary(text, structure, built_year)

    return PropertyRecord(
        source_file_id=file.id,
        source_file_name=file.name,
        property_name=property_name[:120],
        address=address[:200],
        price=price,
        land_area=land_area,
        building_area=building_area,
        structure=structure[:80],
        built_year=built_year[:80],
        station=station[:120],
        walk_minutes=walk_minutes,
        gross_yield=gross_yield,
        annual_rent=annual_rent,
        zoning=zoning[:120],
        road_access=road_access[:120],
        legal_status=legal_status[:120],
        loan_score=score,
        full_loan_possibility=possibility,
        recommended_banks=banks,
        offer_price=offer_price,
        analysis_summary=summary,
        risk_summary=risk,
        raw_text_excerpt=text[:1000],
    )


def score_property(price: int | None, gross_yield: float | None, structure: str, walk_minutes: int | None, land_area: float | None, text: str) -> int:
    score = 40
    if gross_yield is not None:
        if gross_yield >= 9:
            score += 25
        elif gross_yield >= 8:
            score += 18
        elif gross_yield >= 7:
            score += 10
        else:
            score -= 5
    if structure and any(k in structure for k in ["RC", "鉄筋", "鉄骨", "S造"]):
        score += 10
    elif "木造" in structure:
        score += 4
    if walk_minutes is not None:
        score += 10 if walk_minutes <= 10 else 3 if walk_minutes <= 15 else -5
    if land_area and land_area >= 100:
        score += 6
    if price and price <= 100_000_000:
        score += 4
    risk_words = ["再建築不可", "既存不適格", "違法", "私道", "セットバック", "借地", "告知事項"]
    score -= sum(8 for word in risk_words if word in text)
    return max(0, min(100, score))


def recommend_banks(address: str, structure: str, score: int) -> str:
    base = ["大阪信用金庫", "大阪厚生信用金庫", "大阪商工信用金庫", "近畿産業信用組合", "関西みらい銀行"]
    if "京都" in address:
        base.insert(0, "京都中央信用金庫")
    if "兵庫" in address or "神戸" in address:
        base.insert(0, "兵庫信用金庫")
    if score < 55:
        base.append("日本政策金融公庫（小口・修繕資金の相談）")
    if "RC" in structure or "鉄筋" in structure:
        base.append("地銀・信金の長期融資枠")
    return "、".join(dict.fromkeys(base[:6]))


def build_summary(name: str, price: int | None, gross_yield: float | None, possibility: str, score: int) -> str:
    price_text = f"{price:,}円" if price else "価格未抽出"
    yield_text = f"{gross_yield:.2f}%" if gross_yield is not None else "利回り未抽出"
    return f"{name} は {price_text} / 表面利回り {yield_text}。融資スコアは {score}/100、フルローン可能性は {possibility}。"


def build_risk_summary(text: str, structure: str, built_year: str) -> str:
    found = [w for w in ["再建築不可", "既存不適格", "違法", "私道", "セットバック", "借地", "告知事項", "ハザード"] if w in text]
    notes = []
    if found:
        notes.append("要確認キーワード: " + "、".join(found))
    if not structure:
        notes.append("構造が未抽出のため耐用年数確認が必要")
    if not built_year:
        notes.append("築年が未抽出のため融資期間確認が必要")
    return "。".join(notes) if notes else "大きなリスクキーワードは自動検出されていません。接道・法令・修繕履歴は別途確認してください。"

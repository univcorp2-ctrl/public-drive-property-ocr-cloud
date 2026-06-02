import math
import re
from typing import Any

JAPANESE_ZONINGS = [
    "第一種低層住居専用地域",
    "第二種低層住居専用地域",
    "第一種中高層住居専用地域",
    "第二種中高層住居専用地域",
    "第一種住居地域",
    "第二種住居地域",
    "準住居地域",
    "田園住居地域",
    "近隣商業地域",
    "商業地域",
    "準工業地域",
    "工業地域",
    "工業専用地域",
]


def _find_number(pattern: str, text: str) -> float | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return float(match.group(1)) if match else None


def _find_percent(label_pattern: str, text: str) -> float | None:
    return _find_number(rf"(?:{label_pattern})[^0-9]{{0,20}}([0-9]{{2,4}}(?:\.[0-9]+)?)\s*%?", text)


def _extract_address(text: str) -> str | None:
    for line in text.splitlines():
        if any(label in line for label in ["所在地", "住所", "地番"]):
            return re.sub(r"^(所在地|住所|地番)\s*[:：]?\s*", "", line).strip()
    return None


def _extract_zoning(text: str) -> str | None:
    for zoning in JAPANESE_ZONINGS:
        if zoning in text:
            return zoning
    match = re.search(r"用途地域\s*[:：]?\s*([^\n\r]+)", text)
    return match.group(1).strip() if match else None


def _road_far_multiplier(zoning: str | None) -> float:
    if zoning and any(keyword in zoning for keyword in ["商業", "工業"]):
        return 0.6
    return 0.4


def analyze_volume(text: str) -> dict[str, Any]:
    land_area = _find_number(r"([0-9]+(?:\.[0-9]+)?)\s*(?:㎡|m2|m²|平米)", text)
    tsubo = _find_number(r"([0-9]+(?:\.[0-9]+)?)\s*坪", text)
    if land_area is None and tsubo is not None:
        land_area = tsubo * 3.305785

    building_coverage_ratio = _find_percent("建ぺい率|建蔽率|BCR", text)
    floor_area_ratio = _find_percent("容積率|FAR", text)
    road_width = _find_number(r"(?:前面道路|道路幅員|幅員)[^0-9]{0,20}([0-9]+(?:\.[0-9]+)?)\s*m", text)
    avg_unit_size = _find_number(
        r"(?:平均住戸面積|平均住戸|1戸|一戸)[^0-9]{0,20}([0-9]+(?:\.[0-9]+)?)\s*(?:㎡|m2|m²|平米)",
        text,
    )
    avg_unit_size = avg_unit_size or 45.0
    zoning = _extract_zoning(text)

    road_limited_far = None
    applied_far = floor_area_ratio
    if road_width is not None:
        road_limited_far = road_width * _road_far_multiplier(zoning) * 100
        if applied_far is not None and road_width < 12:
            applied_far = min(applied_far, road_limited_far)

    footprint = None
    total_floor_area = None
    rentable_area = None
    estimated_floors = None
    estimated_units = None

    if land_area is not None and building_coverage_ratio is not None:
        footprint = land_area * building_coverage_ratio / 100

    if land_area is not None and applied_far is not None:
        total_floor_area = land_area * applied_far / 100
        rentable_area = total_floor_area * 0.82
        estimated_units = max(1, math.floor(rentable_area / avg_unit_size))

    if footprint and total_floor_area:
        estimated_floors = max(1, math.ceil(total_floor_area / footprint))

    missing = []
    for key, value in {
        "土地面積": land_area,
        "建ぺい率": building_coverage_ratio,
        "容積率": floor_area_ratio,
        "前面道路幅員": road_width,
        "用途地域": zoning,
    }.items():
        if value is None:
            missing.append(key)

    confidence = max(0.2, 1.0 - 0.13 * len(missing))
    cautions = [
        "この結果は初期検討用の概算であり、建築可否・収益性・法適合を保証しません。",
        "斜線制限、日影規制、高度地区、防火地域、条例、接道、敷地形状は別途確認してください。",
    ]
    if road_limited_far is not None and floor_area_ratio is not None and applied_far != floor_area_ratio:
        cautions.append("前面道路幅員による容積率制限を反映しています。")
    if missing:
        cautions.append(f"不足項目: {', '.join(missing)}")

    return {
        "address": _extract_address(text),
        "zoning": zoning,
        "inputs": {
            "land_area_m2": round(land_area, 2) if land_area is not None else None,
            "building_coverage_ratio_percent": building_coverage_ratio,
            "floor_area_ratio_percent": floor_area_ratio,
            "road_width_m": road_width,
            "avg_unit_size_m2": avg_unit_size,
        },
        "calculation": {
            "road_limited_far_percent": round(road_limited_far, 2)
            if road_limited_far is not None
            else None,
            "applied_far_percent": round(applied_far, 2) if applied_far is not None else None,
            "max_footprint_m2": round(footprint, 2) if footprint is not None else None,
            "max_total_floor_area_m2": round(total_floor_area, 2)
            if total_floor_area is not None
            else None,
            "estimated_rentable_area_m2": round(rentable_area, 2) if rentable_area is not None else None,
            "estimated_floors": estimated_floors,
            "estimated_units": estimated_units,
        },
        "confidence": round(confidence, 2),
        "cautions": cautions,
    }

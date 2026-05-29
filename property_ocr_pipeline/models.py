from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


@dataclass(slots=True)
class DriveFile:
    id: str
    name: str
    mime_type: str
    modified_time: str = ""
    local_path: str = ""


@dataclass(slots=True)
class PropertyRecord:
    source_file_id: str
    source_file_name: str
    property_name: str = "未抽出"
    address: str = ""
    price: int | None = None
    land_area: float | None = None
    building_area: float | None = None
    structure: str = ""
    built_year: str = ""
    station: str = ""
    walk_minutes: int | None = None
    gross_yield: float | None = None
    annual_rent: int | None = None
    zoning: str = ""
    road_access: str = ""
    legal_status: str = ""
    loan_score: int = 0
    full_loan_possibility: str = "要確認"
    recommended_banks: str = ""
    offer_price: int | None = None
    analysis_summary: str = ""
    risk_summary: str = ""
    raw_text_excerpt: str = ""
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AnalysisRun:
    run_type: str
    status: str
    files_scanned: int
    files_analyzed: int
    new_properties: int
    summary: str
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

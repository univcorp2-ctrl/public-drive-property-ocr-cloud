from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_session_and_analyze_flow() -> None:
    session_response = client.post("/api/session", json={"note_id": "demo-note-001"})
    assert session_response.status_code == 200
    token = session_response.json()["token"]

    manual_text = """所在地: 東京都サンプル区1-2-3
土地面積: 180.25㎡
用途地域: 第一種住居地域
建ぺい率: 60%
容積率: 300%
前面道路幅員: 4.0m
平均住戸面積: 45㎡
"""
    response = client.post(
        "/api/analyze",
        data={"token": token, "manual_text": manual_text},
        files={"file": ("plan.txt", b"dummy", "text/plain")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["inputs"]["land_area_m2"] == 180.25
    assert payload["result"]["calculation"]["applied_far_percent"] == 160.0
    assert set(payload["exports"].keys()) == {"csv", "xlsx", "txt"}


def test_invalid_note_id_rejected() -> None:
    response = client.post("/api/session", json={"note_id": "not-allowed"})
    assert response.status_code == 403

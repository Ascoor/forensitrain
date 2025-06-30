from fastapi.testclient import TestClient
from app.main import app


async def _fake_lookup(number: str):
    return {
        "status": "success",
        "data": {"phone_number": number},
        "errors": None,
        "timestamp": "2024-01-01T00:00:00Z",
    }


async def _fake_enrich(number: str):
    return {
        "status": "success",
        "data": {"phone": number, "confidence_score": 1.0},
        "errors": None,
        "timestamp": "2024-01-01T00:00:00Z",
    }


def test_analyze_phone(monkeypatch):
    from app.routers import phone as phone_router

    monkeypatch.setattr(phone_router, "multi_source_lookup", _fake_lookup)
    client = TestClient(app)
    resp = client.post("/api/phone/analyze", json={"phone_number": "123"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"


def test_enrich_phone(monkeypatch):
    from app.routers import phone as phone_router

    monkeypatch.setattr(phone_router, "a_enrich_phone_data", _fake_enrich)
    client = TestClient(app)
    resp = client.post("/api/phone/enrich", json={"phone_number": "123"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

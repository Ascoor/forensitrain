from fastapi.testclient import TestClient
from app.main import app


def _fake_smart(phone: str):
    return {"dummy": True}


def _fake_footprint(phone: str):
    return {"metadata": {"phone": phone}}


def test_smart_lookup(monkeypatch):
    from app.routers import osint as osint_router

    monkeypatch.setattr(osint_router, "smart_osint_lookup", _fake_smart)
    client = TestClient(app)
    resp = client.post("/api/osint/smart-lookup", json={"phone": "123"})
    assert resp.status_code == 200
    assert resp.json()["data"]["dummy"]


def test_osint_footprint(monkeypatch):
    from app.routers import osint as osint_router

    monkeypatch.setattr(osint_router, "extract_osint_footprint", _fake_footprint)
    client = TestClient(app)
    resp = client.post("/api/osint/footprint", json={"phone": "123"})
    assert resp.status_code == 200
    assert resp.json()["data"]["metadata"]["phone"] == "123"

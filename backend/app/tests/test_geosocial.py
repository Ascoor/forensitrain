from fastapi.testclient import TestClient
from app.main import app


async def _fake_extract(username: str):
    return {
        "tweets": [{"latitude": 1, "longitude": 2, "text": "hi", "created_at": "now"}]
    }


def test_geosocial(monkeypatch):
    from app.routers import geosocial as geosocial_router

    monkeypatch.setattr(geosocial_router, "extract_footprint", _fake_extract)
    client = TestClient(app)
    resp = client.post("/api/geosocial/footprint", json={"username": "user"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["data"]["count"] == 1

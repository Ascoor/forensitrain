from fastapi.testclient import TestClient
from app.main import app


async def _fake_scan(handle: str):
    return {
        "status": "success",
        "data": {"profiles": ["example"]},
        "errors": None,
        "timestamp": "2024-01-01T00:00:00Z",
    }


def test_deep_scan(monkeypatch):
    from app.routers import social as social_router

    monkeypatch.setattr(social_router, "deep_social_scan", _fake_scan)
    client = TestClient(app)
    resp = client.post("/api/social/deep-scan", json={"handle": "user"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

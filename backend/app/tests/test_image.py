from fastapi.testclient import TestClient
from app.main import app


async def _fake_analyze(data: bytes):
    return {
        "faces_detected": 0,
        "objects": [],
        "text": "",
        "exif": None,
    }


def test_analyze_image(monkeypatch):
    from app.routers import image as image_router

    monkeypatch.setattr(image_router, "a_analyze_image_bytes", _fake_analyze)
    client = TestClient(app)
    resp = client.post("/api/analyze-image", files={"file": ("test.jpg", b"data")})
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

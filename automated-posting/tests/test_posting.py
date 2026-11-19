from fastapi.testclient import TestClient
from app.main import app
from app.services import posting_service
from app.schemas import PlatformResult

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_rejects_message_over_200_characters():
    response = client.post("/posting", json={"message": "x" * 201})
    assert response.status_code == 422

def test_rejects_no_link():
    response = client.post("/posting", json={"message": "Hello world"})
    assert response.status_code == 422

def test_rejects_two_links():
    response = client.post("/posting", json={"message": "Visit https://one.example and https://two.example"})
    assert response.status_code == 422

def test_accepts_one_valid_link(monkeypatch):
    async def fake_publish(message):
        return [
            PlatformResult(platform="Mock", status="success", posted_url="https://example.com/post/1",
                           public_access=True, date="2026-11-17", time="10:00:00")
        ]
    monkeypatch.setattr(posting_service, "publish_to_all", fake_publish)
    response = client.post("/posting", json={"message": "Visit our site https://example.com"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["results"][0]["status"] == "success"

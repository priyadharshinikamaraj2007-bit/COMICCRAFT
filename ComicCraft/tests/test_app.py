from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "ComicCraft" in response.text

def test_generate_renders_comic_preview(monkeypatch):
    comic = {
        "character_name": "Alex",
        "prompt": "A forest adventure",
        "pdf_url": "/export/comic.pdf",
        "panels": [],
    }
    monkeypatch.setattr("app.routes.create_comic", lambda data: comic)

    response = client.post("/generate", data={"prompt": comic["prompt"]})

    assert response.status_code == 200
    assert "Alex's Story" in response.text
    assert "A forest adventure" in response.text

def test_json_validation():
    response = client.post("/generate-comic/json", json={"prompt": "x"})
    assert response.status_code == 422

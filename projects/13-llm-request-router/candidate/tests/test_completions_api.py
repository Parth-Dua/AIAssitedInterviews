from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_completion_endpoint_basic():
    response = client.post("/completions", json={"prompt": "api-test-prompt-1"})
    assert response.status_code == 200
    body = response.json()
    assert body["from_cache"] is False
    assert body["model"]
    assert body["text"]


def test_completion_rejects_empty_prompt():
    response = client.post("/completions", json={"prompt": ""})
    assert response.status_code == 422

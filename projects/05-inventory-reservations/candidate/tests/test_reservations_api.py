from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_default_pagination_returns_items():
    response = client.get("/reservations")
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 10  # default limit
    assert body["next_cursor"] is not None


def test_category_filter_returns_only_that_category():
    """Feature request from the warehouse app team: filter the reservations
    list down to a single category.
    """
    response = client.get("/reservations", params={"category": "electronics", "limit": 10})
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) > 0
    assert all(item["category"] == "electronics" for item in body["items"])


def test_unknown_category_returns_empty_results():
    response = client.get("/reservations", params={"category": "does-not-exist", "limit": 10})
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["next_cursor"] is None

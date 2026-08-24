from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_run_batch_endpoint_single_worker():
    response = client.post(
        "/batches/run",
        json={"batch_id": "api-batch-1", "job_count": 4, "num_workers": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["batch_id"] == "api-batch-1"
    assert body["remaining"] == 0
    assert body["finalize_count"] == 1


def test_run_batch_rejects_zero_job_count():
    response = client.post(
        "/batches/run",
        json={"batch_id": "api-batch-2", "job_count": 0, "num_workers": 1},
    )
    assert response.status_code == 422

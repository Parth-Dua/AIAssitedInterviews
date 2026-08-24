from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _create_job(payload=None):
    response = client.post("/jobs", json={"payload": payload or {}})
    assert response.status_code == 200
    return response.json()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_create_and_get_job_starts_queued():
    job = _create_job({"rows": [1, 2]})
    assert job["status"] == "queued"
    assert job["attempt_count"] == 0

    fetched = client.get(f"/jobs/{job['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "queued"


def test_start_and_finish_job_via_api_happy_path():
    job = _create_job({"rows": [1, 2, 3]})

    start_resp = client.post(f"/jobs/{job['id']}/start")
    assert start_resp.status_code == 200
    assert start_resp.json()["status"] == "running"
    assert start_resp.json()["attempt_count"] == 1

    finish_resp = client.post(
        f"/jobs/{job['id']}/finish", json={"result": "export-final.csv"}
    )
    assert finish_resp.status_code == 200
    body = finish_resp.json()
    assert body["status"] == "completed"
    assert body["result"] == "export-final.csv"


def test_finish_rejects_body_with_both_result_and_error():
    job = _create_job({"rows": [1]})
    client.post(f"/jobs/{job['id']}/start")

    response = client.post(
        f"/jobs/{job['id']}/finish",
        json={"result": "export.csv", "error": "boom"},
    )
    assert response.status_code == 422


def test_cancel_queued_job_is_accepted():
    """Product has asked for the ability to cancel a job that hasn't been
    picked up by a worker yet (see README's feature request).
    """
    job = _create_job({"rows": [1]})

    response = client.post(f"/jobs/{job['id']}/cancel")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_cancel_running_job_is_rejected_via_api():
    job = _create_job({"rows": [1]})
    client.post(f"/jobs/{job['id']}/start")

    response = client.post(f"/jobs/{job['id']}/cancel")

    assert response.status_code == 409
    assert client.get(f"/jobs/{job['id']}").json()["status"] == "running"


def test_duplicate_finish_via_api_is_rejected():
    job = _create_job({"rows": [1]})
    client.post(f"/jobs/{job['id']}/start")
    client.post(f"/jobs/{job['id']}/finish", json={"result": "export-first.csv"})

    response = client.post(
        f"/jobs/{job['id']}/finish", json={"result": "export-second.csv"}
    )

    assert response.status_code == 409
    fetched = client.get(f"/jobs/{job['id']}")
    assert fetched.json()["result"] == "export-first.csv"

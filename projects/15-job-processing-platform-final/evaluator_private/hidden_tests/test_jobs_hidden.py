"""Hidden tests. Copy this file into candidate/tests/ (it is not present in
the candidate repo) and run `pytest` from candidate/ after applying a
candidate's fix, or after applying reference_solution/ to validate the
answer key.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.job_repository import JobRepository
from app.services.job_service import InvalidJobStateError, JobService

client = TestClient(app)


def make_service() -> JobService:
    return JobService(JobRepository())


def _create_job(payload=None):
    response = client.post("/jobs", json={"payload": payload or {}})
    return response.json()


# ---------------------------------------------------------------------------
# Generalizing the duplicate-finish fix beyond the "completed" case.
# ---------------------------------------------------------------------------


def test_duplicate_finish_after_failed_is_also_rejected():
    service = make_service()
    job = service.create_job({"rows": []})
    service.start_job(job.id)
    service.finish_job(job.id, result=None, error="first failure")

    with pytest.raises(InvalidJobStateError):
        service.finish_job(job.id, result=None, error="second-stale-failure")

    reloaded = service.get_job(job.id)
    assert reloaded.status == "failed"
    assert reloaded.error == "first failure"


# ---------------------------------------------------------------------------
# cancel_job must enforce the same "only from queued" rule the reported bug
# was about, not just accept a queued job and stop there.
# ---------------------------------------------------------------------------


def test_cancel_running_job_is_rejected():
    service = make_service()
    job = service.create_job({"rows": [1]})
    service.start_job(job.id)

    with pytest.raises(InvalidJobStateError):
        service.cancel_job(job.id)

    assert service.get_job(job.id).status == "running"


def test_cancel_completed_job_is_rejected():
    service = make_service()
    job = service.create_job({"rows": [1]})
    service.start_job(job.id)
    service.finish_job(job.id, result="export-x.csv", error=None)

    with pytest.raises(InvalidJobStateError):
        service.cancel_job(job.id)

    assert service.get_job(job.id).status == "completed"


def test_cancel_failed_job_is_rejected():
    service = make_service()
    job = service.create_job({"rows": [1]})
    service.start_job(job.id)
    service.finish_job(job.id, result=None, error="boom")

    with pytest.raises(InvalidJobStateError):
        service.cancel_job(job.id)

    assert service.get_job(job.id).status == "failed"


def test_cancel_already_cancelled_job_is_rejected():
    service = make_service()
    job = service.create_job({"rows": [1]})
    service.cancel_job(job.id)

    with pytest.raises(InvalidJobStateError):
        service.cancel_job(job.id)


def test_api_cancel_running_job_returns_409():
    job = _create_job({"rows": [1]})
    client.post(f"/jobs/{job['id']}/start")

    response = client.post(f"/jobs/{job['id']}/cancel")

    assert response.status_code == 409


# ---------------------------------------------------------------------------
# start_job's guard gap: the same missing-check mistake as the reported bug,
# just on a different transition. Partial-credit generalization check.
# ---------------------------------------------------------------------------


def test_start_already_completed_job_is_rejected():
    service = make_service()
    job = service.create_job({"rows": [1]})
    service.start_job(job.id)
    service.finish_job(job.id, result="export-x.csv", error=None)

    with pytest.raises(InvalidJobStateError):
        service.start_job(job.id)

    reloaded = service.get_job(job.id)
    assert reloaded.status == "completed"
    assert reloaded.attempt_count == 1


def test_api_start_already_completed_job_returns_409():
    job = _create_job({"rows": [1]})
    client.post(f"/jobs/{job['id']}/start")
    client.post(f"/jobs/{job['id']}/finish", json={"result": "export-x.csv"})

    response = client.post(f"/jobs/{job['id']}/start")

    assert response.status_code == 409


# ---------------------------------------------------------------------------
# A cancelled job is terminal, same as completed/failed.
# ---------------------------------------------------------------------------


def test_cancelled_job_cannot_be_started_or_finished():
    service = make_service()
    job = service.create_job({"rows": [1]})
    service.cancel_job(job.id)

    with pytest.raises(InvalidJobStateError):
        service.start_job(job.id)

    with pytest.raises(InvalidJobStateError):
        service.finish_job(job.id, result="export-x.csv", error=None)

    reloaded = service.get_job(job.id)
    assert reloaded.status == "cancelled"
    assert reloaded.attempt_count == 0

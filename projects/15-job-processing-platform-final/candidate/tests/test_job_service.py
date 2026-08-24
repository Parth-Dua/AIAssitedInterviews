import pytest

from app.repositories.job_repository import JobRepository
from app.services.job_service import InvalidJobStateError, JobService


def make_service() -> JobService:
    return JobService(JobRepository())


def test_start_then_finish_success_sets_completed_with_result():
    service = make_service()
    job = service.create_job({"rows": [1, 2, 3]})
    service.start_job(job.id)

    finished = service.finish_job(job.id, result="export-abc123.csv", error=None)

    assert finished.status == "completed"
    assert finished.result == "export-abc123.csv"
    assert finished.error is None


def test_start_then_finish_failure_sets_failed_with_error():
    service = make_service()
    job = service.create_job({"rows": []})
    service.start_job(job.id)

    finished = service.finish_job(job.id, result=None, error="export backend timed out")

    assert finished.status == "failed"
    assert finished.error == "export backend timed out"
    assert finished.result is None


def test_finish_queued_job_that_never_started_is_rejected():
    service = make_service()
    job = service.create_job({"rows": [1]})

    with pytest.raises(InvalidJobStateError):
        service.finish_job(job.id, result="export-early.csv", error=None)


def test_duplicate_finish_does_not_overwrite_completed_result():
    """Reported by support: a job's result changed on its own, minutes
    after it had already completed successfully with the right file. The
    worker fleet's callback delivery is documented as at-least-once, not
    exactly-once (see README) — the same 'job finished' callback can
    arrive more than once for a given job.
    """
    service = make_service()
    job = service.create_job({"rows": [1, 2]})
    service.start_job(job.id)
    service.finish_job(job.id, result="export-first-correct.csv", error=None)

    with pytest.raises(InvalidJobStateError):
        service.finish_job(job.id, result="export-second-stale.csv", error=None)

    reloaded = service.get_job(job.id)
    assert reloaded.status == "completed"
    assert reloaded.result == "export-first-correct.csv"

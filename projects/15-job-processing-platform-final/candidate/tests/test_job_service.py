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


def test_duplicate_finish_does_not_overwrite_failed_job():
    """Same class of bug as the reported one, but landing on the 'failed'
    terminal state instead of 'completed' — a fix that only special-cases
    'completed' would miss this.
    """
    service = make_service()
    job = service.create_job({"rows": [1, 2]})
    service.start_job(job.id)
    service.finish_job(job.id, result=None, error="export backend timed out")

    with pytest.raises(InvalidJobStateError):
        service.finish_job(job.id, result="export-late.csv", error=None)

    reloaded = service.get_job(job.id)
    assert reloaded.status == "failed"
    assert reloaded.error == "export backend timed out"
    assert reloaded.result is None


def test_start_already_running_job_is_rejected():
    """start_job had no status guard at all, so a duplicate/late 'start'
    callback could silently reset an already-running job's attempt count.
    """
    service = make_service()
    job = service.create_job({"rows": [1]})
    service.start_job(job.id)

    with pytest.raises(InvalidJobStateError):
        service.start_job(job.id)

    reloaded = service.get_job(job.id)
    assert reloaded.attempt_count == 1


def test_start_completed_job_is_rejected():
    service = make_service()
    job = service.create_job({"rows": [1]})
    service.start_job(job.id)
    service.finish_job(job.id, result="export-abc.csv", error=None)

    with pytest.raises(InvalidJobStateError):
        service.start_job(job.id)


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
    service.finish_job(job.id, result="export-abc.csv", error=None)

    with pytest.raises(InvalidJobStateError):
        service.cancel_job(job.id)


def test_cancel_already_cancelled_job_is_rejected():
    service = make_service()
    job = service.create_job({"rows": [1]})
    service.cancel_job(job.id)

    with pytest.raises(InvalidJobStateError):
        service.cancel_job(job.id)


def test_cancelled_job_cannot_later_be_started_or_finished():
    """A cancelled job is terminal, same as completed/failed."""
    service = make_service()
    job = service.create_job({"rows": [1]})
    service.cancel_job(job.id)

    with pytest.raises(InvalidJobStateError):
        service.start_job(job.id)

    with pytest.raises(InvalidJobStateError):
        service.finish_job(job.id, result="export-abc.csv", error=None)

    assert service.get_job(job.id).status == "cancelled"

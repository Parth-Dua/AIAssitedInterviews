from app.services.job_batch_tracker import JobBatchTracker
from app.services.job_service import JobService


def make_service() -> tuple[JobService, JobBatchTracker]:
    tracker = JobBatchTracker()
    return JobService(tracker), tracker


async def test_single_worker_batch_finalizes_exactly_once():
    service, tracker = make_service()
    result = await service.run_batch("batch-1", job_count=5, num_workers=1)

    assert result.remaining == 0
    assert result.finalize_count == 1
    assert tracker.call_count("batch-1") == 5


async def test_mark_job_done_called_exactly_job_count_times():
    """Regardless of the final remaining/finalize numbers, every job that
    goes through a worker must invoke mark_job_done exactly once. This
    rules out an off-by-one in the worker loop as the cause of any
    completion-count discrepancy.
    """
    service, tracker = make_service()
    await service.run_batch("batch-2", job_count=6, num_workers=3)

    assert tracker.call_count("batch-2") == 6


async def test_multi_worker_batch_finalizes_once_when_all_jobs_complete():
    """Reproduces the reported bug: running a batch across more than one
    worker, every job completes, but the batch never finalizes.
    """
    service, tracker = make_service()
    result = await service.run_batch("batch-3", job_count=2, num_workers=2)

    assert tracker.call_count("batch-3") == 2
    assert result.remaining == 0
    assert result.finalize_count == 1

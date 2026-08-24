from __future__ import annotations

import asyncio

from app.models.schemas import BatchResult
from app.services.job_batch_tracker import JobBatchTracker
from app.services.job_queue import Job, JobQueue
from app.services.worker import worker_loop


class JobService:
    """Orchestrates running one batch of jobs across a pool of workers."""

    def __init__(self, tracker: JobBatchTracker | None = None):
        self._tracker = tracker if tracker is not None else JobBatchTracker()

    async def run_batch(
        self, batch_id: str, job_count: int, num_workers: int
    ) -> BatchResult:
        self._tracker.start_batch(batch_id, job_count)

        queue = JobQueue()
        for _ in range(job_count):
            queue.put_nowait(Job(batch_id=batch_id))
        for _ in range(num_workers):
            queue.put_nowait(None)

        await asyncio.gather(
            *(worker_loop(queue, self._tracker) for _ in range(num_workers))
        )

        return BatchResult(
            batch_id=batch_id,
            remaining=self._tracker.remaining(batch_id),
            finalize_count=self._tracker.finalize_count(batch_id),
        )

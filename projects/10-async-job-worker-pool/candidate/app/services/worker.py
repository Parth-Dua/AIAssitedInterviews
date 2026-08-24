from __future__ import annotations

import asyncio

from app.services.job_batch_tracker import JobBatchTracker
from app.services.job_queue import JobQueue


async def worker_loop(queue: JobQueue, tracker: JobBatchTracker) -> None:
    """Pull jobs off the queue and process them until this worker's stop
    signal arrives.
    """
    while True:
        job = await queue.get()
        if job is None:
            return

        await asyncio.sleep(0)  # stand-in for the actual unit of work
        await tracker.mark_job_done(job.batch_id)

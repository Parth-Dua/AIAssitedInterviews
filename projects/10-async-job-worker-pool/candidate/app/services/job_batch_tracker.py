from __future__ import annotations

import asyncio


class JobBatchTracker:
    """Tracks per-batch job completion.

    A batch is started with a known job count. Each time a job in that
    batch finishes, callers report it via ``mark_job_done``. A batch's
    completion must be finalized exactly once, at the moment the last of
    its jobs finishes — no more, no less, regardless of how many workers
    are reporting completions for the batch at the same time.
    """

    def __init__(self) -> None:
        self._remaining: dict[str, int] = {}
        self._finalize_count: dict[str, int] = {}
        self._call_count: dict[str, int] = {}

    def start_batch(self, batch_id: str, job_count: int) -> None:
        self._remaining[batch_id] = job_count
        self._finalize_count.setdefault(batch_id, 0)
        self._call_count.setdefault(batch_id, 0)

    async def mark_job_done(self, batch_id: str) -> None:
        self._call_count[batch_id] = self._call_count.get(batch_id, 0) + 1

        remaining = self._remaining[batch_id]
        await asyncio.sleep(0)
        remaining -= 1
        self._remaining[batch_id] = remaining
        if remaining == 0:
            self._finalize_count[batch_id] = self._finalize_count.get(batch_id, 0) + 1

    def remaining(self, batch_id: str) -> int:
        return self._remaining.get(batch_id, 0)

    def finalize_count(self, batch_id: str) -> int:
        return self._finalize_count.get(batch_id, 0)

    def call_count(self, batch_id: str) -> int:
        return self._call_count.get(batch_id, 0)

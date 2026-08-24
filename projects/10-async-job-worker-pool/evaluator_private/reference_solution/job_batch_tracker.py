"""Reference fix (primary): reorder mark_job_done so there is no await
between the read and the write of the shared counter — the read-decrement-
write-and-check sequence for a given batch_id now runs as one atomic,
uninterruptible step of the event loop, so no other task can observe a
stale `remaining` value. The simulated "persist progress" await moves
after the state has already been updated, where its timing no longer
matters. This is a drop-in replacement for
candidate/app/services/job_batch_tracker.py.

An equally acceptable alternative — keeping the await inside the critical
section but protecting it with a single shared instance-level
asyncio.Lock() — is provided in
job_batch_tracker_lock_variant.py for comparison. See bug_design.md for
why both are correct and why a *new* Lock() created inside each call
(the tempting-but-wrong fix) is not.
"""

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

        remaining = self._remaining[batch_id] - 1
        self._remaining[batch_id] = remaining
        if remaining == 0:
            self._finalize_count[batch_id] = self._finalize_count.get(batch_id, 0) + 1

        await asyncio.sleep(0)  # stand-in for the actual unit of work

    def remaining(self, batch_id: str) -> int:
        return self._remaining.get(batch_id, 0)

    def finalize_count(self, batch_id: str) -> int:
        return self._finalize_count.get(batch_id, 0)

    def call_count(self, batch_id: str) -> int:
        return self._call_count.get(batch_id, 0)

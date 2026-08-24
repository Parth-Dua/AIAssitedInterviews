"""Reference fix (alternative): keep the await inside the critical section
(e.g. because a real "persist progress" call genuinely needs to happen
before the decrement is considered durable) and instead protect the whole
read-modify-write-and-check block with a single SHARED, INSTANCE-LEVEL
asyncio.Lock() created once in __init__ and held via `async with
self._lock:` on every call. Because the lock is shared across all calls
(and, here, across all batch_ids — a coarser but still correct choice),
a second concurrent mark_job_done for the same batch_id has to wait for
the first to finish before it can read `remaining`, closing the race
window. This is a drop-in replacement for
candidate/app/services/job_batch_tracker.py.

Contrast with the tempting-but-wrong fix documented in bug_design.md,
which creates a *new* asyncio.Lock() inside each call instead of reusing
one shared lock — that provides no mutual exclusion at all.
"""

from __future__ import annotations

import asyncio


class JobBatchTracker:
    def __init__(self) -> None:
        self._remaining: dict[str, int] = {}
        self._finalize_count: dict[str, int] = {}
        self._call_count: dict[str, int] = {}
        self._lock = asyncio.Lock()

    def start_batch(self, batch_id: str, job_count: int) -> None:
        self._remaining[batch_id] = job_count
        self._finalize_count.setdefault(batch_id, 0)
        self._call_count.setdefault(batch_id, 0)

    async def mark_job_done(self, batch_id: str) -> None:
        self._call_count[batch_id] = self._call_count.get(batch_id, 0) + 1

        async with self._lock:
            remaining = self._remaining[batch_id]
            await asyncio.sleep(0)  # stand-in for the actual unit of work
            remaining -= 1
            self._remaining[batch_id] = remaining
            if remaining == 0:
                self._finalize_count[batch_id] = (
                    self._finalize_count.get(batch_id, 0) + 1
                )

    def remaining(self, batch_id: str) -> int:
        return self._remaining.get(batch_id, 0)

    def finalize_count(self, batch_id: str) -> int:
        return self._finalize_count.get(batch_id, 0)

    def call_count(self, batch_id: str) -> int:
        return self._call_count.get(batch_id, 0)

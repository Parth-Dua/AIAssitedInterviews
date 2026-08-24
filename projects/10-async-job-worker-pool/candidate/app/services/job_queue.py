from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    """A single unit of work belonging to a batch (e.g. one image to resize,
    one email to send). No real work is performed in this exercise.
    """

    batch_id: str


class JobQueue:
    """Thin wrapper around ``asyncio.Queue`` that workers pull jobs from.

    A ``None`` entry is a stop signal for exactly one worker: producers put
    one ``None`` per worker onto the queue after all real jobs, and each
    worker exits after it receives its own ``None``.
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue[Job | None] = asyncio.Queue()

    def put_nowait(self, item: Job | None) -> None:
        self._queue.put_nowait(item)

    async def get(self) -> Job | None:
        return await self._queue.get()

    def qsize(self) -> int:
        return self._queue.qsize()

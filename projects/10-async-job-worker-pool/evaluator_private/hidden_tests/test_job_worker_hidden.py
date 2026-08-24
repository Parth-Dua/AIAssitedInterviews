"""Hidden tests. Copy this file into candidate/tests/ (it is not present in
the candidate repo) and run `pytest -q` from candidate/ after applying a
candidate's fix, or after applying reference_solution/job_batch_tracker.py
(or job_batch_tracker_lock_variant.py) to validate the answer key.

These are NOT expected to pass against the original buggy
job_batch_tracker.py — they exist to (a) confirm a fix generalizes beyond
the exact numbers in the public failing test, (b) catch the tempting-but-
incomplete "new Lock() per call" fix, and (c) confirm a fix is correct
across multiple concurrent, distinct batches (without penalizing a
correct-but-coarser single global lock).
"""

import asyncio

from app.services.job_batch_tracker import JobBatchTracker
from app.services.job_service import JobService


def make_service() -> tuple[JobService, JobBatchTracker]:
    tracker = JobBatchTracker()
    return JobService(tracker), tracker


async def test_race_generalizes_to_different_job_and_worker_counts():
    """Same race, different numbers than the public failing test — a fix
    that only special-cases 2 jobs / 2 workers should not pass this.
    """
    service, tracker = make_service()
    result = await service.run_batch("hidden-batch-1", job_count=6, num_workers=3)

    assert tracker.call_count("hidden-batch-1") == 6
    assert result.remaining == 0
    assert result.finalize_count == 1


async def test_new_lock_per_call_does_not_provide_exclusion():
    """Catches the tempting-but-wrong fix of creating a fresh
    asyncio.Lock() inside mark_job_done on every call instead of reusing
    one shared, instance-level lock. A per-call lock is never contended
    (every caller gets its own, uncontended lock), so it changes nothing
    about the scheduling and the batch still fails to finalize correctly.
    Both acceptable fixes (reorder-so-no-await-in-the-critical-section, or
    a real shared lock) must pass this.
    """
    service, tracker = make_service()
    result = await service.run_batch("hidden-batch-2", job_count=4, num_workers=2)

    assert tracker.call_count("hidden-batch-2") == 4
    assert result.remaining == 0
    assert result.finalize_count == 1


async def test_concurrent_distinct_batches_do_not_cross_contaminate():
    """Multiple different batch_ids running concurrently must each end up
    with their own correct remaining/finalize counts. A correct fix that
    uses one coarse, shared lock across all batches is fine here (it's
    still correct, just less concurrent) — this test only fails on an
    implementation that actually produces the wrong numbers, e.g. by
    accidentally sharing counters across batch_ids or by only fixing the
    race for a single batch at a time.
    """
    service, tracker = make_service()

    results = await asyncio.gather(
        service.run_batch("hidden-batch-A", job_count=4, num_workers=2),
        service.run_batch("hidden-batch-B", job_count=6, num_workers=3),
        service.run_batch("hidden-batch-C", job_count=3, num_workers=1),
    )
    by_id = {r.batch_id: r for r in results}

    assert by_id["hidden-batch-A"].remaining == 0
    assert by_id["hidden-batch-A"].finalize_count == 1
    assert tracker.call_count("hidden-batch-A") == 4

    assert by_id["hidden-batch-B"].remaining == 0
    assert by_id["hidden-batch-B"].finalize_count == 1
    assert tracker.call_count("hidden-batch-B") == 6

    assert by_id["hidden-batch-C"].remaining == 0
    assert by_id["hidden-batch-C"].finalize_count == 1
    assert tracker.call_count("hidden-batch-C") == 3

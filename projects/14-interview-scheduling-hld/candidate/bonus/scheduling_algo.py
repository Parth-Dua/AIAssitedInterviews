"""Bonus (optional): common free-slot finder.

See README.md in this directory for the full spec. This file only gives you
the function signature; the body is up to you.
"""

from __future__ import annotations


def find_common_free_slots(
    busy_intervals_per_person: list[list[tuple[int, int]]],
    work_hours: tuple[int, int],
    min_duration_minutes: int,
) -> list[tuple[int, int]]:
    """Given each person's busy intervals (as (start_minute, end_minute)
    offsets within a single day) and the shared work-hours window, return
    the list of (start, end) slots, each at least min_duration_minutes
    long, where EVERY person is free simultaneously, in chronological
    order, non-overlapping.
    """
    raise NotImplementedError

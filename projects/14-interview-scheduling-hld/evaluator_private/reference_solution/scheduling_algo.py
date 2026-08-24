"""Reference solution for the bonus find_common_free_slots exercise.

Approach: the set of moments where EVERY person is free is exactly the
complement (within work_hours) of the UNION of everyone's busy intervals —
if any one person is busy, the group isn't simultaneously free, regardless
of who else is free. So: flatten every person's busy intervals into one
list, merge overlapping/touching intervals, then walk the gaps between
merged busy blocks (and before the first / after the last) within
work_hours, keeping only gaps at least min_duration_minutes long.
"""

from __future__ import annotations


def find_common_free_slots(
    busy_intervals_per_person: list[list[tuple[int, int]]],
    work_hours: tuple[int, int],
    min_duration_minutes: int,
) -> list[tuple[int, int]]:
    work_start, work_end = work_hours
    if work_start >= work_end or min_duration_minutes <= 0:
        return []

    # Flatten every person's busy intervals into one list, clipped to the
    # work-hours window (a busy interval that pokes outside work_hours only
    # matters for the part of it that overlaps the window).
    all_intervals: list[tuple[int, int]] = []
    for person_busy in busy_intervals_per_person:
        for start, end in person_busy:
            if end <= start:
                continue
            clipped_start = max(start, work_start)
            clipped_end = min(end, work_end)
            if clipped_start < clipped_end:
                all_intervals.append((clipped_start, clipped_end))

    if not all_intervals:
        # Nobody is ever busy: the entire work-hours window is free.
        if work_end - work_start >= min_duration_minutes:
            return [(work_start, work_end)]
        return []

    all_intervals.sort()
    merged = [all_intervals[0]]
    for start, end in all_intervals[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:  # overlapping or back-to-back -> merge
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))

    free_slots: list[tuple[int, int]] = []
    cursor = work_start
    for busy_start, busy_end in merged:
        if busy_start > cursor:
            gap_end = busy_start
            if gap_end - cursor >= min_duration_minutes:
                free_slots.append((cursor, gap_end))
        cursor = max(cursor, busy_end)

    if cursor < work_end and work_end - cursor >= min_duration_minutes:
        free_slots.append((cursor, work_end))

    return free_slots

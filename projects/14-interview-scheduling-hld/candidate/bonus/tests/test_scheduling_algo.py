"""Public tests for find_common_free_slots. All minute offsets are within a
single day (e.g. 540 = 9:00, 600 = 10:00, using minutes since midnight)."""

from scheduling_algo import find_common_free_slots


def test_single_common_free_slot_between_two_meetings():
    # Person A: busy 9:00-10:00 and 11:00-12:00
    # Person B: busy 9:30-10:30
    # Work hours: 9:00-12:00
    busy = [
        [(540, 600), (660, 720)],
        [(570, 630)],
    ]
    result = find_common_free_slots(busy, work_hours=(540, 720), min_duration_minutes=15)
    assert result == [(630, 660)]


def test_no_one_busy_returns_full_work_hours_window():
    busy = [[], []]
    result = find_common_free_slots(busy, work_hours=(540, 600), min_duration_minutes=30)
    assert result == [(540, 600)]


def test_short_gaps_below_minimum_duration_are_excluded():
    # Gap between meetings is only 10 minutes; min duration required is 15.
    busy = [
        [(540, 600), (610, 660)],
    ]
    result = find_common_free_slots(busy, work_hours=(540, 660), min_duration_minutes=15)
    assert result == []


def test_multiple_free_slots_returned_in_chronological_order():
    busy = [
        [(540, 570), (630, 660), (690, 720)],
    ]
    result = find_common_free_slots(busy, work_hours=(540, 780), min_duration_minutes=20)
    assert result == [(570, 630), (660, 690), (720, 780)]

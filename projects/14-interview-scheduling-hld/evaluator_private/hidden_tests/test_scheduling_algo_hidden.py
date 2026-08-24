"""Hidden tests — Project 14 bonus (find_common_free_slots).

Copy this file into candidate/bonus/tests/ before running `pytest -q` from
candidate/bonus/. Covers the edge cases called out in the brief:
- no common slot exists at all
- a gap exactly at the minimum-duration boundary (inclusive) vs. one minute
  under it (excluded)
- a person with zero busy intervals mixed in with people who have some
- overlapping busy intervals (within one person, and back-to-back across
  different people) that must merge into one continuous busy block
"""

from scheduling_algo import find_common_free_slots


def test_no_common_slot_when_someone_is_busy_the_entire_work_day():
    busy = [
        [(540, 720)],  # person A busy the whole window
        [(600, 630)],  # person B has a gap, but A doesn't
    ]
    result = find_common_free_slots(busy, work_hours=(540, 720), min_duration_minutes=15)
    assert result == []


def test_gap_exactly_at_minimum_duration_boundary_is_included():
    # Gap is exactly 30 minutes; min_duration is also 30 -> inclusive bound.
    busy = [[(540, 600), (630, 700)]]
    result = find_common_free_slots(busy, work_hours=(540, 700), min_duration_minutes=30)
    assert result == [(600, 630)]


def test_gap_one_minute_below_minimum_duration_is_excluded():
    busy = [[(540, 600), (629, 700)]]
    result = find_common_free_slots(busy, work_hours=(540, 700), min_duration_minutes=30)
    assert result == []


def test_person_with_zero_busy_intervals_does_not_block_others_free_time():
    busy = [
        [],  # fully free all day
        [(540, 600)],
        [(650, 700)],
    ]
    result = find_common_free_slots(busy, work_hours=(540, 720), min_duration_minutes=15)
    assert result == [(600, 650), (700, 720)]


def test_overlapping_busy_intervals_within_one_person_are_merged():
    # Same person has two overlapping busy blocks that should merge into one.
    busy = [[(540, 610), (590, 660)]]
    result = find_common_free_slots(busy, work_hours=(540, 720), min_duration_minutes=15)
    assert result == [(660, 720)]


def test_back_to_back_busy_intervals_across_people_merge_with_no_gap():
    # Person A busy 9:00-10:00, Person B busy 10:00-11:00 -> no gap between.
    busy = [
        [(540, 600)],
        [(600, 660)],
    ]
    result = find_common_free_slots(busy, work_hours=(540, 660), min_duration_minutes=15)
    assert result == []


def test_all_people_fully_free_all_day_returns_entire_work_window():
    busy = [[], [], []]
    result = find_common_free_slots(busy, work_hours=(0, 480), min_duration_minutes=60)
    assert result == [(0, 480)]


def test_unsorted_intervals_within_a_person_are_handled_correctly():
    # Intervals given out of order should not affect the result.
    busy = [[(660, 720), (540, 600)]]
    result = find_common_free_slots(busy, work_hours=(540, 780), min_duration_minutes=15)
    assert result == [(600, 660), (720, 780)]

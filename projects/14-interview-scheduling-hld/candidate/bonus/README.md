# Bonus (optional): Common Free-Slot Finder

**This is optional and graded lightly, separately from the design
discussion.** Only come here if you've finished a solid pass at
`DESIGN_WORKSHEET.md` with time to spare. Don't let this eat into your
design-discussion time — a strong design with no bonus attempt beats a
half-finished design with a complete bonus.

## Why this exists

Somewhere under the hood of the system you just designed, something has to
answer "given everyone's busy times, when is the whole panel free?" This is
a small, self-contained version of that computation — good realistic
practice, not a trick question.

## Task

Implement `find_common_free_slots` in `scheduling_algo.py`:

```python
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
```

- `busy_intervals_per_person`: one list of `(start, end)` minute-offset
  intervals per person. A person's intervals may be given out of order, and
  may overlap or be back-to-back with each other — treat any overlapping or
  touching intervals as one continuous busy block. A person can have zero
  busy intervals (free all day).
- `work_hours`: an `(start, end)` window (minute offsets) that bounds the
  day — only slots within this window count, and the window itself is the
  outer bound for the first/last returned slot.
- `min_duration_minutes`: minimum length a returned slot must have. A gap
  of *exactly* this length counts (it's an inclusive bound, not a strict
  one).
- Return slots in chronological order, non-overlapping, each as `(start,
  end)`.
- If no common slot of sufficient length exists, return `[]`.

You don't need to handle multi-day spans, timezones, or anything outside a
single day's minute-offset window — this is intentionally a bounded,
self-contained function.

## Setup

```bash
cd bonus
pip install -e ".[dev]"
```

## Running tests

```bash
cd bonus
pytest -q
```

The public tests in `tests/test_scheduling_algo.py` currently fail with
`NotImplementedError` — that's expected, nothing is implemented yet.

## AI tool policy

Same policy as the main design exercise (see the top-level README and
`.ai/assessment-skill/SKILL.md`): your assistant can help you talk through
the approach, review an attempt, or clarify an edge case — but shouldn't
write the implementation for you.

# Bug + Feature Design (private — do not expose to candidate)

This project bundles a debugging task and a feature-implementation task
that share the same code path, so they're documented together.

## Part A — The pagination bug

### Expected behavior
`GET /reservations?cursor=<id>&limit=<n>` returns up to `limit`
reservations ordered by `sequence` ascending, resuming strictly *after*
`cursor`. Paging through the full collection (following `next_cursor`
until it is `null`) must visit every reservation exactly once — no
duplicates, no gaps.

### Actual (buggy) behavior
`app/repositories/reservation_repository.py::ReservationRepository.list_page`
filters the remaining items with `r.sequence >= cursor` instead of
`r.sequence > cursor`. Since `cursor` is set (by the service) to the
`sequence` of the *last item already returned* on the previous page, the
inclusive comparison re-includes that same item as the first item of the
next page.

### Root cause
Off-by-one / inclusive-boundary error at the repository's cursor filter.
Classic cursor-pagination mistake: the cursor is defined as "the sequence
value of the last item you've already seen," which requires a *strict*
greater-than comparison to resume correctly; the buggy code uses a
non-strict comparison.

### Violated invariant
"A page resumes strictly after the cursor; the item at the cursor position
must never be re-returned." Implied by the bug report and by the natural
meaning of `next_cursor` (a resumption point, not an inclusive start).

### Relevant execution path
`GET /reservations` (`app/api/routes/reservations.py`, thin pass-through)
→ `ReservationService.list_reservations`
(`app/services/reservation_service.py`) → `ReservationRepository.list_page`
(the bug). The candidate must read all three to see that the service's
`next_cursor` computation (`items[-1].sequence if len(items) == limit else
None`) is correct, and that the boundary comparison living in the
repository is the only thing wrong — a good multi-file trace where two
plausible culprits exist and only one is actually broken.

### Evidence available to the candidate
- The bug report's wording maps directly onto a repeatable, deterministic
  test with `limit=5`: page 1 returns ids `[1,2,3,4,5]`, page 2 (using
  `next_cursor=5`) returns `[5,6,7,8,9]` — `5` appears twice.
- Reading `list_page` end-to-end shows exactly one cursor comparison, and
  it uses `>=`.
- Reading the service shows `next_cursor` is set to the *last returned
  item's* sequence, which only makes semantic sense if the next request
  resumes strictly after it.

### Reasonable hypotheses
1. (Correct) The repository's cursor filter is inclusive (`>=`) when it
   should be exclusive (`>`).
2. (Plausible, wrong) The service computes `next_cursor` incorrectly (e.g.
   off-by-one on which item's sequence it uses). Ruled out by reading
   `reservation_service.py`: it always uses the *last* item's `sequence`
   from whatever the repository returned, which is the correct definition
   of a resumption cursor — the repository just doesn't honor it.
3. (Plausible, wrong) The seed data has duplicate `sequence` values.
   Ruled out by inspecting `_seed_reservations()`: sequences are the
   distinct integers 1–18.

### Acceptable fixes
- Change the repository's comparison to `r.sequence > cursor`.
- Equivalent: use `bisect` or an index-based slice that skips past the
  cursor's position rather than re-including it, as long as the net effect
  is a strict resume point.
- `next_cursor` computation in the service should remain untouched — it
  was already correct.

### Tempting but incomplete/wrong fix (bug-only)
Changing the service to subtract one from `next_cursor` before returning
it (e.g. `next_cursor = items[-1].sequence` unchanged, but the *repository*
does `sequence >= cursor + 1`) is functionally equivalent to the correct
fix and is fine. What's **not** fine, and worth flagging if seen: adding a
Python-level `seen_ids` dedup step in the service to filter out
already-returned ids without fixing the repository's comparison — this
requires the service to track cross-request state (defeating the point of
stateless cursor pagination) and is exactly the kind of "papering over the
symptom" fix that should be a red flag in review.

---

## Part B — The category filter feature

### Requested behavior
`GET /reservations` accepts an optional `category` query parameter. When
supplied, results are restricted to reservations with that exact
`category`, while cursor pagination continues to behave correctly *within
the filtered set* — paging through a filtered category must return every
matching item exactly once, with no duplicates and no gaps, using the same
`next_cursor`-until-null contract as the unfiltered case. An unrecognized
category returns an empty result set (`items: []`, `next_cursor: null`),
not an error.

### Starting (incomplete) state
`ReservationService.list_reservations` already accepts a `category`
keyword argument (so calling it directly doesn't crash), but its body
never forwards it to the repository — a `# TODO` comment marks this. The
route (`app/api/routes/reservations.py`) doesn't declare a `category`
query parameter at all yet, so a request like
`GET /reservations?category=electronics` is accepted (FastAPI silently
ignores an undeclared query string key) but has no effect on the response.
This is a realistic "someone stubbed the service signature and then got
pulled onto something else" partially-built-feature state, and it means
the candidate must touch all three layers: add the query parameter to the
route, actually use it in the service, and implement the filtering (plus
fix the pagination bug) in the repository.

### Correct design
Filter by `category` **before** applying the cursor/limit slice, within
the same `list_page` call — i.e., narrow to the matching category first,
then apply the (fixed) cursor boundary and `limit` to that narrowed,
still-`sequence`-ordered list. Because `sequence` values are global and
monotonic regardless of category, filtering first and then comparing
`sequence > cursor` against the filtered list is correct and requires no
separate "filtered sequence" concept — `next_cursor` is still just "the
last returned item's global sequence."

### Tempting but incomplete/wrong implementation
Keep the (fixed) cursor/limit pagination as it already existed — apply
`cursor`/`limit` to the **full, unfiltered** ordered list first, producing
a page of up to `limit` items — and only *then* filter that page down to
the requested `category`:

```python
def list_page(self, cursor, limit, category=None):
    ordered = sorted(self._reservations, key=lambda r: r.sequence)
    if cursor is not None:
        ordered = [r for r in ordered if r.sequence > cursor]
    page = ordered[:limit]
    if category is not None:
        page = [r for r in page if r.category == category]
    return page
```

This is genuinely tempting: it's a one-line addition to already-working
pagination code, it "reads" as filtering by category, and — because the
seed data's first 10 reservations happen to include 4 electronics items —
a quick manual check of page 1 with `category=electronics&limit=10` looks
completely correct (returns electronics items, no obvious problem).

It's incomplete because the page window is chosen from the *unfiltered*
list before the category filter is applied, so:
- A page can come back with fewer than `limit` matching items even though
  more matching items exist further down the unfiltered list (they simply
  weren't inside this request's raw window).
- Worse, the service's `next_cursor` rule (`next_cursor = last item's
  sequence if len(items) == limit else None`) sees the *post-filter*,
  shrunken page length, so as soon as one page's filtered count is less
  than `limit`, pagination reports "no more pages" (`next_cursor: null`)
  even though matching items exist beyond that window — silently
  truncating the traversal.

**Caught by:**
`hidden_tests/test_reservations_hidden.py::test_full_traversal_with_category_filter_collects_exactly_that_categorys_items`
— electronics items are scattered across sequences
`[1, 3, 6, 8, 11, 14, 17]` (7 total), deliberately non-contiguous and more
numerous than the page sizes tested (2, 3, 5). The correct implementation
collects all 7 ids on every page size tested; this incomplete
implementation terminates early and returns fewer.

It's also caught by
`test_category_filter_with_cursor_from_unfiltered_page_does_not_crash`,
which happens to exercise the same flaw from a different angle (a `limit`
larger than the unfiltered window that still excludes a later-appearing
match).

### Validation performed
This tempting-but-incomplete repository implementation was built verbatim
in a temporary copy of the candidate repository (fixed cursor/limit logic,
filter-after-paginate), with `hidden_tests/test_reservations_hidden.py`
copied into `tests/`, and `pytest -q` was run. Result: 10 passed, 2
failed — both failures were exactly the two hidden tests named above; all
8 public tests passed, including the basic
`test_category_filter_returns_only_that_category` (which only checks a
single page's category correctness, not full-traversal completeness) and
`test_pagination_no_duplicates_across_two_pages` (the underlying cursor
bug fix, unaffected by this mistake). This confirms the implementation is
tempting (passes everything visible to the candidate) but incomplete
(fails hidden full-traversal coverage).

### Acceptable implementations
- Filter by category first, then apply the (fixed) cursor/limit slice to
  the filtered list, as in `reference_solution/reservation_repository.py`.
- Equivalent: build the filtered list once and binary-search / index into
  it for the cursor position, as long as filtering happens before the
  cursor/limit windowing.
- Not acceptable: filtering after windowing (see above), or re-deriving
  `next_cursor` from anything other than the last *returned* item's global
  `sequence`.

## Why this is interview-appropriate
This is a very common real-world shape: a small, deterministic pagination
bug (an inclusive vs. exclusive boundary) paired with a natural follow-up
feature request (add a filter) whose main risk is an implementation-order
mistake (filter before vs. after paginating) that looks fine on a single
page and only breaks under full traversal — exactly the kind of thing code
review and “does it work end-to-end, not just on page 1” testing is meant
to catch. No specialist knowledge is required beyond careful reading of
three small files and reasoning about what a cursor means.

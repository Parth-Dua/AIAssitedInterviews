# Expected Reasoning Path

## Bug fix

1. Run `pytest -q`; observe `test_pagination_no_duplicates_across_two_pages`
   fails while most other tests pass.
2. Read the assertion failure output: page 1 is `[1,2,3,4,5]`, page 2 is
   `[5,6,7,8,9]` — item `5` appears in both.
3. Open `app/services/reservation_service.py`; confirm `next_cursor` is set
   to the last returned item's `sequence` (here, `5`), which is then passed
   as `cursor` on the next call.
4. Open `app/repositories/reservation_repository.py::list_page`; find the
   cursor filter `r.sequence >= cursor`. Recognize that a resumption cursor
   defined as "the last item you've already seen" requires a *strict*
   `>` comparison, not `>=`.
5. Change the comparison to `r.sequence > cursor`. Re-run the bug's test;
   it passes. Manually re-derive page 2 (`cursor=5`) and confirm it now
   returns `[6,7,8,9,10]` with no overlap.

## Feature: category filter

6. Re-read the README's feature request and the service's `# TODO`
   comment noting `category` isn't wired through yet. Notice the route
   doesn't even declare a `category` query parameter.
7. Add `category: Optional[str] = None` to the route function signature
   and pass it through to `service.list_reservations(...)`.
8. In the service, stop ignoring `category` — pass it to
   `self._repository.list_page(cursor, limit, category=category)`.
9. In the repository, add a `category` parameter to `list_page`. The key
   design decision: filter by category *before* applying the cursor/limit
   slice, not after — because `next_cursor` is derived from the length of
   whatever `list_page` returns, filtering after slicing can produce a
   short page (and therefore a premature `next_cursor: null`) even though
   more matching items exist further along.
10. Verify manually (or via a quick script): request `category=electronics`
    with a `limit` smaller than the total number of electronics items (7),
    and confirm following `next_cursor` across multiple requests visits
    every electronics item exactly once. This is the check that would have
    caught the "filter after paginate" mistake.
11. Confirm an unrecognized category (e.g. `category=doesnotexist`) returns
    `{"items": [], "next_cursor": null}` rather than an error — this falls
    out naturally from filtering to an empty list, so no special-case code
    should be needed; if a candidate adds a manual `if category not in
    known_categories: raise ...`, that's an unnecessary and riskier
    deviation worth asking about.
12. Add or strengthen tests: a full-traversal-with-category test is the
    single most valuable addition, since it's the only kind of test that
    catches the "looks right on page 1, wrong on page 2+" class of mistake
    in the feature implementation.
13. Re-run the full suite; everything passes. Explain: the pagination bug
    was an inclusive-boundary error in the cursor comparison; the feature
    required threading a new parameter through three layers and, crucially,
    applying it before (not after) the existing pagination slice so the
    two compose correctly.

A strong candidate reaches the bug fix (step 5) within 15-20 minutes and
a working, correctly-ordered feature implementation (step 9) within the
remaining time, leaving room to add the full-traversal test and verify.

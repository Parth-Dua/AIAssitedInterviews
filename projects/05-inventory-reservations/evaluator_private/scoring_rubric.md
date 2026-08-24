# Scoring Rubric — Project 5 (100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the route → service → repository flow; noticed the service already had a `category` parameter (unused) and the route didn't expose one, before editing. |
| Debugging process | 10 | Reproduced the pagination bug via the failing test (or equivalent manual repro) before making changes; didn't shotgun-edit across files. |
| Root-cause reasoning | 15 | Correctly identifies the repository's cursor filter uses an inclusive (`>=`) comparison when it should be exclusive (`>`), and can articulate why a resumption cursor requires strict inequality. |
| Bug-fix correctness | 15 | Public pagination test passes; full-traversal hidden tests pass with no duplicates and no gaps across varied `limit` values; `next_cursor`/service logic left untouched (it was already correct). |
| Feature implementation quality | 20 | `category` query param added to the route; threaded through the service; repository filters by category **before** applying cursor/limit (not after); unrecognized category yields an empty result, not an error, without unnecessary special-case validation code. |
| Tests added | 10 | Added at least one regression test beyond the given failing ones — ideally a full-traversal-with-category-filter test, since that's the only kind of test that would have caught the filter-after-paginate mistake. |
| Scope discipline | 5 | Did not modify the response schema, unrelated endpoints, or seed data; changes stayed within route/service/repository for the bug fix + feature. |
| Communication | 15 | Can clearly state: the pagination bug's root cause and why the fix is correct; why the category filter must be applied before pagination rather than after; what they checked to confirm both work together (e.g. full traversal with a filter active). |

**Passing bar (strong intern/new-grad signal):** ≥75, all hidden tests
pass, and the candidate can explain both the pagination root cause and the
filter-ordering design decision without prompting.

**Red flags:**
- Fix passes the public `test_category_filter_returns_only_that_category`
  test but fails
  `test_full_traversal_with_category_filter_collects_exactly_that_categorys_items`
  (the "paginate first, filter the page second" incomplete implementation —
  see `bug_design.md`).
- Candidate fixes the pagination bug but never implements the category
  feature, or vice versa — this exercise has two deliverables and both are
  graded.
- Candidate "fixes" the duplicate-item bug by de-duplicating results in the
  service (e.g. tracking seen ids) instead of correcting the repository's
  boundary comparison — passes the given test but doesn't fix the actual
  logic error and would misbehave under concurrent/stateless requests.
- Candidate adds explicit `if category not in {"electronics", ...}: raise
  HTTPException(404)`-style validation instead of letting an unrecognized
  category fall out naturally as an empty result — contradicts the stated
  requirement and hardcodes a category list that will drift from the data.
- Candidate cannot explain *why* either fix is correct, only that changing
  X made a test pass.

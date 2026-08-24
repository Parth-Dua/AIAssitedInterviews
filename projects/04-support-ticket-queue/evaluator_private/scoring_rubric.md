# Scoring Rubric — Project 4 (100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the API→service→domain→repository flow and specifically when the route omits vs. passes `watchers` before editing. |
| Debugging process | 15 | Reproduced the bug via the two failing tests (or equivalent manual repro, e.g. checking object identity across tickets) before making changes; didn't shotgun-edit. |
| Root-cause reasoning | 20 | Correctly identifies the mutable default argument (`watchers: list[str] = []`) combined with in-place mutation (`.append`) as the cause, and can articulate *why* this results in a shared, growing list across calls that omit the argument — not just "something about the watchers list." |
| Correctness of fix | 25 | Public tests pass; all hidden tests pass, including the caller-list-mutation test; `watchers` lists are independent objects per ticket; auto-watch email still applied on every path. |
| Tests added/improved | 10 | Added at least one regression test beyond the two given failing ones, or meaningfully strengthened existing coverage (e.g., object-identity check, caller-list-mutation check). |
| Scope discipline | 5 | Did not modify unrelated files/behavior (API shape, repository, domain object) without justification. |
| Communication / explanation | 15 | Can clearly state expected vs. actual behavior, the mutable-default-argument root cause in their own words, why the fix is correct, and what they checked to rule out breaking other behavior (including the caller-mutation subtlety). |

**Passing bar (strong intern/new-grad signal):** ≥75, hidden tests pass
(including the caller-list-mutation test), and candidate can explain the
mutable-default-argument mechanism without prompting.

**Red flags:**
- Fix passes the two originally-failing tests but fails
  `test_create_ticket_does_not_mutate_caller_supplied_watchers_list` (the
  "`None` sentinel but still appends in place" incomplete fix — see
  `bug_design.md`).
- Candidate cannot explain *why* the bug happened beyond "changing the
  default to `None` fixed it," with no understanding of shared object
  identity or in-place mutation.
- Candidate rewrites large parts of the service or repository "to be
  safe" (e.g., adds a database, changes the repository to deep-copy
  everything) instead of a minimal, targeted fix.
- Candidate "fixes" it by having `add_watcher` create a new list from
  scratch each time rather than addressing `create_ticket` — this only
  papers over one symptom and still leaves newly created tickets sharing
  state (the second failing test would still fail).

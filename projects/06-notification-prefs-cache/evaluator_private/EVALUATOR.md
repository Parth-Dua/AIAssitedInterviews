# Evaluator Guide — Project 6: Notification Preferences Cache

## Format & target
AI-Assisted Debugging + Feature Implementation Assessment. SWE Intern / New
Grad / Backend. ~60-75 min. Difficulty 7/10.

## How to grade

1. Read the candidate's diff across
   `app/services/notification_prefs_service.py` and `app/cache/cache.py`
   (and any other files they touched — flag if they touched unrelated
   files, e.g. `app/repositories/notification_prefs_repository.py`,
   `app/models/schemas.py`, or the route).
2. Copy `hidden_tests/test_notification_prefs_hidden.py` into
   `candidate/tests/` and run `pytest -q` from `candidate/`. All public +
   hidden tests should pass for a fully correct submission (19 total: 14
   public + 5 hidden).
3. Compare their bug fix and TTL implementation against
   `reference_solution/` and `bug_design.md`'s "Acceptable fixes" /
   "Acceptable implementations" sections — several phrasings are fine,
   only the semantics matter (invalidate-or-correctly-repopulate on write;
   TTL expiry checked and evicted in `get()`; injectable clock).
4. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of root cause, feature design, and
   verification.
5. Score with `scoring_rubric.md`.
6. Ask 2-3 questions from `DEBRIEF.md`, covering both the bug and the
   feature.

## Interview-realism audit (private)

1. **Format simulated:** AI-assisted debugging-plus-feature OA / second-
   round backend interview. A step up from a pure debugging exercise
   (Projects 1-4) and comparable in shape to Project 5 — one reported bug
   plus one requested feature sharing the same code path — but here the
   bug is a cache-consistency bug rather than a pagination boundary bug,
   and the feature (TTL with an injectable clock) requires more careful
   design than a query-parameter filter.
2. **Role level:** Intern / new grad / early-career backend.
3. **Why feasible in 60-75 min:** Small, three-file execution path for the
   bug (route → service → cache/repository); the bug itself is a one-line
   omission (a missing cache-invalidation call) with a clear failing test.
   The TTL feature touches two files (`Cache` and the service's read
   path) and is conceptually simple once a candidate accepts "don't use
   real sleeps, inject the clock" — which the starting code already
   half-sets-up via the `now_fn` parameter already present on `Cache.__init__`.
   A candidate who reads carefully should find the bug in 15-20 minutes
   and have 35-45 minutes left for the TTL feature plus tests.
4. **Signal obtained:** Whether the candidate can (a) recognize a
   cache/source-of-truth divergence bug from a plausible bug report and
   fix it symmetrically with the existing read path, and (b) design and
   implement time-based cache expiry using dependency injection for the
   clock rather than reaching for real sleeps — and, more subtly, whether
   they think to cache *what was persisted* rather than *what was
   requested* once a server-side normalization rule is in play.
5. **Coding vs. reasoning split:** ~40% coding (a 1-3 line bug fix + a
   small, two-file TTL feature), ~60% reasoning/design/verification —
   consistent with the "implementation" project type and comparable to
   Project 5's split.
6. **Would a top company use a close variant:** Yes — "here's a cache in
   front of a data store with a missing invalidation on write, and here's
   a request to add TTL-based expiry as defense in depth" is an extremely
   common real-world backend interview and real-sprint-ticket shape,
   arguably one of the most common production bug categories in general.
7. **Anything included for production education rather than signal?** No
   — the injectable clock (`now_fn`) exists purely so TTL behavior is
   testable without real sleeps, and this is called out explicitly in the
   README/docstrings so it doesn't read as an unexplained quirk; the "keep
   at least one channel enabled" normalization rule exists specifically to
   set up the tempting-but-incomplete-fix distinction (cache the request
   vs. cache the persisted value), not as an arbitrary product detail.

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, fix the reported
bug, and implement the requested TTL feature." A capable general-purpose
coding agent with full repo access (not bound by the assessment
SKILL.md) can plausibly one-shot the missing-invalidation bug (a clear
failing test pins it down precisely) and the basic TTL mechanics (checking
expiry in `get()`, using the already-present `now_fn`). However, an agent
optimizing for "avoid an extra repository round-trip" is meaningfully
likely to reach for `cache.set(key, <value built from the request>)`
instead of `cache.delete(key)` (or `cache.set(key, saved, ...)`) when
fixing the write path — which looks correct and passes every visible
check unless the agent specifically reasons about (or is prompted to
verify) the case where server-side normalization changes the persisted
value relative to the request. This is exactly the signal this project is
designed to capture.

This is expected and acceptable for a *Level 2 (harder debugging + code
modification)* project — the interview signal is not "can the AI find the
bug" but "does the candidate direct their assistant to verify that the
cache reflects what was actually persisted, not just what was requested,
and can they explain why that distinction matters in general." Under the
assessment SKILL.md, the assistant is constrained not to hand over the
diff outright, which restores the intended signal: the candidate still
has to drive the design decision and verify it themselves. See
`ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.

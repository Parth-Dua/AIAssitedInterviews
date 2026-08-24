# Evaluator Guide — Project 11: Rate Limiter LLD

## Format & target
Low-Level Design + Implementation. Backend SWE, mid-level and up. ~60-90 min.
Difficulty 7/10.

## How to grade

1. Confirm both parts are implemented: `candidate/ratelimiter/token_bucket.py`,
   `fixed_window.py`, and `tiered.py` no longer raise `NotImplementedError`.
2. Copy `hidden_tests/test_rate_limiter_hidden.py` into `candidate/tests/`
   and run `pytest -q` from `candidate/`. All public + hidden tests should
   pass for a fully correct, well-designed solution.
3. Specifically check the three hidden tests using `AlwaysAllowLimiter` /
   `AlwaysDenyLimiter` / `CountingLimiter` — these are the objective check
   for the isinstance-branching pitfall (see `bug_design.md`). If these
   three fail while everything else passes, the candidate's
   `TieredRateLimiter` is very likely branching on concrete types instead of
   depending on the interface; open `tiered.py` and confirm.
4. Review whether Part 2 required modifying Part 1 code
   (`token_bucket.py`). Check the candidate's diff/commit history if
   available, or ask directly in the debrief. **This is itself a design
   signal, not just a pass/fail gate** — a candidate whose Part 1 needed no
   changes to support Part 2 demonstrated that their original design
   anticipated the kind of change a follow-up requirement introduces, which
   is the actual thing this exercise is testing.
5. Compare the candidate's class design against
   `reference_solution/ratelimiter/` and `expected_reasoning.md` — several
   internal designs are fine (dataclass vs. tuple vs. small nested class for
   per-key state, etc.); only the externally-observable behavior and the
   polymorphism requirement are hard constraints.
6. Score with `scoring_rubric.md`.
7. Ask 2-3 questions from `DEBRIEF.md`.

## Interview-realism audit (private)

1. **Format simulated:** LLD/OOD coding round — implement a small library
   from an interface and a requirements doc, with a follow-up requirement
   revealed mid-exercise. This is a very standard shape for backend LLD
   interviews (as distinct from a pure whiteboard-only OOD round — this one
   is code-and-tests, which many companies now run this way).
2. **Role level:** Mid-level backend SWE and up; also reasonable for a
   strong new grad in a system-design-adjacent loop.
3. **Why feasible in 60-90 min:** Part 1 is a self-contained, well-scoped
   token bucket (a well-known algorithm many candidates have seen) with a
   given class skeleton and given public tests describing exact expected
   behavior. Part 2 reuses the same interface and clock-injection pattern
   established in Part 1, so it's mostly new surface area, not new
   concepts. A candidate who paces well should finish core implementation
   in 45-60 minutes, leaving time to add tests and articulate reasoning.
4. **Signal obtained:** Whether the candidate can (a) implement a
   moderately fiddly stateful algorithm correctly against a given
   interface and testability constraint (clock injection), and (b) design
   a dispatcher that depends only on an abstraction rather than quietly
   coupling to concrete types — the single most common LLD-interview
   failure mode when a "pluggable strategy" requirement shows up.
5. **Coding vs. reasoning split:** ~55% coding (three classes, real logic
   in each), ~45% design reasoning/verification (why the interface was
   respected, what would need to change to add a fourth strategy, what
   concurrency would require).
6. **Would a top company use a close variant:** Yes — rate limiters
   (token bucket specifically) are one of the most frequently cited LLD
   interview questions across large tech companies; the "add a second
   strategy without touching the first" follow-up is a common and
   realistic extension interviewers add live.
7. **Anything included for production education rather than signal:** No —
   the clock-injection requirement is included purely because it's the
   only way to make time-based logic deterministically testable in a timed
   assessment, not as a lesson in itself. The FastAPI wrapper in `api/` is
   explicitly optional/non-graded and exists only for scenario realism.

## AI-trivialization check

Tested prompt: "Implement TokenBucketRateLimiter, FixedWindowRateLimiter,
and TieredRateLimiter per the README, make all tests pass." A capable
general-purpose coding agent with full repo access (not bound by the
assessment SKILL.md) can very plausibly produce a fully correct, properly
polymorphic solution in one or two shots — token bucket and fixed window
are extremely well-represented algorithms in training data, and the
`RateLimiter` interface plus the explicit Part 2 wording ("without any
calling code needing to know which strategy is in use") strongly primes a
capable model toward pure delegation over isinstance-branching.

This is expected and acceptable for a *Level 1-2 (fundamentals)* LLD
project — same posture as Project 1's debugging exercise. The interview
signal is not "can the AI produce a correct design" but "can the candidate
drive that design themselves, explain their own class boundaries, and
recognize (with or without AI help) why the polymorphism requirement
matters." Under the assessment SKILL.md, the assistant is constrained to
discuss design tradeoffs and review code rather than write the
implementation outright, which restores the intended signal: the candidate
still has to make and defend the actual design decisions. See
`ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's implementation, added tests, and design explanation only.

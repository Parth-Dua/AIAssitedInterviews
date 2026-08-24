# Evaluator Guide — Project 13: LLM Request Router

## Format & target
AI-Assisted Debugging + Feature Implementation Assessment. SWE Intern / New
Grad / Backend. ~75-90 min. Difficulty 8/10.

## How to grade

1. Read the candidate's diff to `app/services/llm_router_service.py` (and
   any other files they touched — flag if they touched
   `app/clients/fake_model_client.py`, `app/cache/response_cache.py`, or
   `app/models/schemas.py`, since none of those should need to change).
2. Copy `hidden_tests/test_llm_router_hidden.py` into `candidate/tests/`
   and run `pytest -q` from `candidate/`. All public + hidden tests should
   pass for a fully correct submission (12 total: 8 public + 4 hidden).
3. Compare their bug fix and validation implementation against
   `reference_solution/llm_router_service.py` and `bug_design.md`'s
   "Acceptable fixes" / "Acceptable implementations" sections — several
   phrasings are fine, only the semantics matter (fallback results never
   cached; both models' responses independently validated for
   blankness).
4. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of root cause, feature design, and
   verification.
5. Score with `scoring_rubric.md`.
6. Ask 2-3 questions from `DEBRIEF.md`, covering both the bug and the
   feature.

## Interview-realism audit (private)

1. **Format simulated:** AI-assisted debugging-plus-feature OA / second-
   round backend interview, using an AI-inference-gateway framing as the
   domain.
2. **Role level:** Intern / new grad / early-career backend.
3. **Why feasible in 75-90 min:** A small, four-file execution path for
   the bug (route → service → client/cache), all of it pure Python with no
   real I/O; the bug itself is a one-line-too-many mistake (an extra,
   unconditional cache write) with a clear failing test that reproduces
   the exact reported scenario. The validation feature touches only the
   service file and follows a pattern the candidate has already seen once
   in the code (the existing `except ModelUnavailableError` retry
   handling) — it's "do the same thing again for a different failure
   mode," not a new mechanism. A candidate who reads
   `llm_router_service.py` and `fake_model_client.py` carefully should
   find the bug in 20-25 minutes and have 50-65 minutes left for the
   validation feature plus tests.
4. **Signal obtained:** Whether the candidate can (a) recognize a
   cache-write-policy bug — caching a result regardless of which upstream
   actually produced it — from a plausible bug report and fix it without
   either narrowly patching the symptom or overcorrecting into removing a
   legitimate caching behavior, and (b) extend a retry/fallback loop to
   treat a second, distinct class of upstream failure (a malformed-but-
   not-erroring response) the same way it already treats an outright
   exception, including the "both paths exhausted" terminal case.
5. **Coding vs. reasoning split:** ~35% coding (a small conditional fix +
   a retry-loop extension, all within one file), ~65% reasoning/design/
   verification — consistent with the "implementation" project type and
   comparable to Projects 6-8's split.
6. **Would a top company use a close variant:** Yes — "retry an unreliable
   upstream N times, fall back to a secondary provider, cache the good
   result but never the degraded one, and validate the response shape
   before trusting it" is one of the most common real-world backend
   interview and production-incident shapes there is; the AI-inference
   framing is a current, recognizable example of it, not a special case
   requiring ML knowledge.
7. **Anything included for production-education rather than signal?** No
   — `FakeModelClient`'s `unavailable_prompts`/`blank_response_prompts`
   test hooks exist purely so both failure modes are deterministically
   reproducible without real timing or randomness, and this is explained
   plainly in the module's docstring and the README rather than left as
   an unexplained quirk; the two-call-site cache-write bug and the
   two-model validation requirement both exist specifically to create the
   distinct, testable "acceptable vs. overcorrected/incomplete" fix
   boundaries this exercise is built to measure, not as arbitrary
   flourishes.

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, fix the reported
bug, and implement the requested validation feature." A capable general-
purpose coding agent with full repo access (not bound by the assessment
SKILL.md) can plausibly locate and fix the cache-write bug in one shot
(the failing test pins the exact scenario down precisely), and can
plausibly implement the "blank primary response retries" half of the
validation feature by pattern-matching the existing
`except ModelUnavailableError` handling. However, an agent that stops
there — validating the primary but not thinking to apply the identical
check to the fallback's response — produces code that looks complete,
passes every *public* test, and only fails the hidden
`test_both_primary_and_fallback_blank_raises_no_valid_completion` test,
which is exactly the gap this project is designed to probe. An agent is
also meaningfully likely to reach for "just add a TTL to the cache" as a
first instinct for the bug report (TTLs are a very common pattern-matched
response to "stale cache" complaints), which resolves the symptom's
severity but not its root cause, and which a candidate directing the
agent needs to push back on.

This is expected and acceptable for a *Level 2-3 (harder debugging + code
modification)* project — the interview signal is not "can the AI find the
bug," it's "does the candidate direct their assistant to verify the fix
against the *general* invariant (fallback results are never cached, under
any prompt or retry count) rather than the one reported instance, and do
they think to ask 'what if the fallback is also broken?' rather than
stopping once the primary's blank-response case works." Under the
assessment SKILL.md, the assistant is constrained not to hand over the
diff outright, which restores the intended signal: the candidate still
has to drive the design decisions (why not just a TTL; validate which
paths) and verify them itself. See `ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.

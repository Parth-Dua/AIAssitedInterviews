# Evaluator Guide — Project 17: Order Notification Service

## Format & target
AI-Assisted Debugging Assessment. SWE Intern / New Grad / Backend. ~45-60
min. Difficulty 7/10 — calibrated to Amazon-style repo-based debugging OAs
(second project of the Node/Express track, following Project 16's
async/error-handling-flavored companion; same template used through
Project 20).

## How to grade

1. Read the candidate's diff to `src/controllers/orderController.ts` (and
   any other files they touched — flag if they touched unrelated files,
   e.g. `warehouseNotifier.ts`'s offline-set logic, `orderRepository.ts`,
   or `validateOrderCreate.ts`'s validation rules).
2. Copy `hidden_tests/orderHidden.test.ts` into `candidate/tests/` and run
   `npm test` from `candidate/` after applying a candidate's fix. All
   public + hidden tests should pass for a fully correct fix.
3. Compare their fix against `reference_solution/` and `bug_design.md`'s
   "Acceptable fixes" section — a `try/catch` + `next(err)` fix and an
   `asyncHandler`-style wrapper utility are both fine; only the semantics
   (rejection reaches `errorHandler.ts`) matter.
4. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of root cause and verification.
5. Score with `scoring_rubric.md`.
6. Ask 2-3 questions from `DEBRIEF.md`.

## Interview-realism audit (private)

1. **Format simulated:** Amazon-style repo-based debugging OA — a small,
   unfamiliar multi-layer Express/TypeScript service, a plain-English bug
   report about a hung request, public tests that partially reproduce it
   (via a bounded race, not a real hang), hidden tests that probe for an
   incomplete fix.
2. **Role level:** Intern / new grad / early-career backend (SDE1-leaning).
3. **Why feasible in 45-60 min:** A single missing `try/catch`/`next(err)`
   forwarding in one small function, five small supporting files (route,
   two middleware, service, notifier) that are each trivial to read, one
   failing test that already reproduces the bug precisely and fast. A
   candidate who reads `createOrder` carefully should locate the missing
   rejection-handling in 10-20 minutes, leaving time to fix, verify the
   error contract, test, and explain.
4. **Signal obtained:** Whether the candidate understands how Express 4
   handles (or fails to handle) promise rejections from async route
   handlers, can trace a request through several thin layers to rule out
   two plausible-but-wrong hypotheses (middleware ordering, the notifier
   itself hanging) by actually reading/testing the relevant code, and
   produces a fix that both resolves the hang *and* preserves the app's
   established error-response contract rather than stopping at "a response
   goes out now."
5. **Coding vs. reasoning split:** ~25% coding (a few-line `try/catch` +
   `next(err)` fix, or a small wrapper utility, plus a test or two), ~75%
   reasoning/verification — this is a slightly more reasoning-heavy split
   than Project 16 because the "obviously wrong" surface fix (catch and
   respond directly) is very easy to write and very easy to mistake for
   complete.
6. **Would a top company use a close variant:** Yes — "an async Express
   route handler swallows a rejected promise from a downstream call,
   leaving the client hanging; find and fix it *properly*, not just make a
   response go out" is one of the most common real Express interview/code
   -review shapes for backend/full-stack roles, and it directly tests
   whether a candidate understands the specific Express 4 vs. Express 5
   behavioral difference rather than pattern-matching a generic
   try/catch.
7. **Anything included for production education rather than signal?** No —
   the fake `warehouseNotifier` (standing in for a real HTTP client), the
   in-memory `Map` repository, and the thin controller/service split are
   included only because they're the minimal realistic shape of a small
   Express service that talks to an external system, not as a lesson in
   Express idioms for their own sake.

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, identify the
defect, and fix it." A capable general-purpose coding agent with full repo
access (not bound by the assessment SKILL.md) can plausibly find and fix
the literal missing-`next(err)` issue in one shot, since the one failing
test pins it down fairly precisely and "async Express handler doesn't
forward promise rejections" is an extremely well-represented pattern in
training data — this mirrors Project 16's finding for the equivalent
merge-bug tier. What is *not* trivially one-shotted even by an unconstrained
agent is the second half: recognizing that a naive `try { ... } catch (err)
{ res.status(500).send('failed') }` "fix" is incomplete because it bypasses
the app's actual error contract (`errorHandler.ts`'s `502` +
`{ error: { code, message } }` shape) — nothing in the repo or the one
failing public test points at this directly; only the hidden test does,
which the agent doesn't have access to, and a plausible naive agent
completion genuinely reaches for `res.status(500).send(...)` as a "good
enough" fix. This is expected and acceptable for a *Level 1-2 (Node-track
fundamentals)* project: the interview signal is not "can the AI find the
literal missing catch" but "can the candidate direct their assistant well,
verify the suggested fix against the app's actual conventions (not just
'does a response come back now'), and think past the first green test run."
Under the assessment SKILL.md, the assistant is constrained not to just hand
over the diff, which restores the intended signal: the candidate still has
to drive reproduction, hypothesis confirmation, and verification themselves,
including deciding whether "the hang is gone" actually means "the bug is
fully and correctly fixed." See `ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.

# Backend Interview Practice Suite — Curriculum

A private, 22-project curriculum simulating real software-engineering interviews and
online assessments (SWE Intern / New Grad / Backend / AI-Engineering-with-SWE-signal).
Projects 1-15 are Python/FastAPI. Projects 16-20 are Node.js/TypeScript/Express,
purpose-built for Amazon-style repo-based debugging OAs (see §"Node/Express track"
below). Projects 21-22 are a **black-box full-app debugging** tier (see §"Black-box
full-app debugging tier" below) — a structurally different, deliberately
above-typical-OA-difficulty pair meant for skill *development*, not just assessment
practice. Same underlying candidate/evaluator_private convention throughout.

Every project lives at `projects/NN-slug/` and contains:

- `candidate/` — the repo you actually work in (app, tests, README, AI skill file)
- `evaluator_private/` — answer key, hidden tests, rubric (do not open until you're done)

Run `cat PROGRESS.md` to log attempts. Do not open `evaluator_private/` before attempting
a project — it contains the root cause, reference solution, and hidden tests.

## How to use this suite

1. `cd projects/NN-slug/candidate`
2. Read `README.md` — treat it exactly like a real interview/OA prompt.

**Environment note:** if `pip install -e ".[dev]"` reports everything satisfied but
plain `pytest` then fails with `ModuleNotFoundError`, your `pytest` executable is
probably resolving to a different Python environment than the one the dependencies were
installed into. Use `python3 -m pytest -q` instead — it runs pytest via the same
interpreter `pip3`/`pip install` targeted.
3. If you want AI assistance, load `.ai/assessment-skill/SKILL.md` into whatever coding
   assistant you use (Claude, Cursor, Copilot, Codex, Gemini, etc.) as a system/project
   instruction. It constrains the assistant to interview-appropriate help.
4. Timebox yourself to the stated duration.
5. Run the public tests (`pytest`) as you work.
6. When done, open `../evaluator_private/EVALUATOR.md` and self-grade honestly, then run
   the hidden tests and compare against the rubric.
7. Log the attempt in `PROGRESS.md`.

## Project Index

| # | Project | Format | Type | Difficulty | Time | Main Skills |
|---|---------|--------|------|------------|------|--------------|
| 1 | OrderFlow Pricing Service | AI-Assisted Debugging | Debugging | 5/10 | 45-60m | API→service→repo chain reasoning, data transformation bugs |
| 2 | Library Loan Tracker | AI-Assisted Debugging | Debugging | 5/10 | 45-60m | SQL/SQLAlchemy query correctness, date/time handling |
| 3 | Profile Settings API | AI-Assisted Debugging | Debugging | 6/10 | 45-60m | API contract mismatch, partial-update (PATCH) semantics |
| 4 | Support Ticket Queue | AI-Assisted Debugging | Debugging | 6/10 | 45-60m | Object/state bugs, mutable-default aliasing |
| 5 | Inventory Reservations | Debugging + Feature | Debugging/Implementation | 6/10 | 60-75m | Pagination/filtering, multi-layer changes |
| 6 | Notification Preferences Cache | Debugging + Feature | Debugging/Implementation | 7/10 | 60-75m | Cache invalidation, tempting-but-incomplete fixes |
| 7 | Team Workspace Permissions | Debugging + Feature | Debugging/Implementation | 7/10 | 60-75m | AuthZ/ownership bugs, role extension |
| 8 | Coupon Redemption Service | Debugging + Feature | Debugging/Implementation | 7/10 | 60-75m | State-transition bugs, competing hypotheses, backward compatibility |
| 9 | Payment Webhook Handler | Advanced Debugging | Debugging | 8/10 | 60-90m | Idempotency, duplicate delivery, passes-basic-fails-edge |
| 10 | Async Job Worker Pool | Advanced Debugging | Debugging | 8/10 | 60-90m | asyncio concurrency, race conditions, competing root causes |
| 11 | Rate Limiter Library | Low-Level Design | LLD | 7/10 | 60-90m | Pluggable strategy design, extensibility, follow-up requirement |
| 12 | Feature Flag Rule Engine | Low-Level Design | LLD | 8/10 | 60-90m | Rule composition, evaluation state, follow-up requirement |
| 13 | LLM Request Router | AI-Engineering Backend | Debugging/Implementation | 8/10 | 75-90m | Fallback/retry, deterministic fakes, response caching, async |
| 14 | Interview Scheduling Service | System Design | HLD | 6/10 (SWE-level) | 45-60m | API/data model, scaling basics, caching, failure handling |
| 15 | Job Processing Platform (Final) | Integrated Debugging | Debugging (+small feature) | 9/10 | 75-90m | Multi-layer root cause, state machine, verification, follow-ups |
| 16 | Team Task Board API (Node) | AI-Assisted Debugging | Debugging | 6/10 | 45-60m | Express route→controller→service→repo reasoning, partial-update merge bugs |
| 17 | Order Notification Service (Node) | AI-Assisted Debugging | Debugging | 7/10 | 45-60m | Async Express route error handling, middleware ordering, competing hypotheses |
| 18 | Shared Playlist API (Node) | Debugging + Feature | Debugging/Implementation | 7/10 | 60-75m | Uniqueness-check bugs, cursor vs. offset pagination |
| 19 | Product Price Lookup Service (Node) | Advanced Debugging | Debugging | 8/10 | 60-75m | Cache-key construction, external client abstraction, fallback reasoning |
| 20 | Expense Approval Platform (Final, Node) | Integrated Debugging | Debugging (+feature) | 8.5/10 | 60-90m | Coarse vs. resource-level authorization, feature-driven generalization |
| 21 | TeamNotes (Black-Box) | Black-Box Full-App Debugging | Debugging | 8.5-9/10 | 90m | Discover-through-usage, optimistic concurrency, one invariant / two symptoms |
| 22 | Neighborhood Marketplace (Black-Box, Final) | Black-Box Full-App Debugging | Debugging | 9/10 | 105m | Discover-through-usage, cache/lazy-expiry divergence, rejecting an incomplete fix |

**Distribution:** 8 debugging-heavy (1,2,3,4,5,6,7,9 primary; 15 counted as debugging-heavy
final), 3 implementation/feature-extension (5,6,8 have substantial feature work; 13 is
implementation-heavy), 2 LLD (11,12), 1 AI-engineering backend (13), 1 HLD (14). Projects
5-8 and 15 deliberately combine debugging with implementation, matching real interview
loops. Projects 16-20 (Node/Express) add a second debugging-heavy cluster calibrated
specifically to Amazon-style repo-debugging OAs: 16-17 are pure debugging, 18 is
debugging+feature, 19 is advanced multi-layer debugging, 20 is an integrated final
capstone — mirroring the shape of the Python 1→15 progression at a compressed scale.

Difficulty rises 1→15, then rises again 16→20 within the Node track (the Node track is
not a continuation of the Python difficulty numbers — 16 is comparable to Python's
fundamentals tier, not to Python 15/16-in-sequence). Projects 21-22 sit above BOTH
tracks deliberately — they're the hardest and second-hardest projects in the whole
curriculum, on purpose, as a capstone skill-building pair rather than assessment
calibration (see below). Do 1-20 roughly in order the first time through; revisit any
project where your process (not just your final diff) felt weak; attempt 21-22 only
once you're comfortable with everything else. If you're specifically practicing for a
Node/Express-based OA (e.g. Amazon-style), you can go straight to 16-20 without doing
1-15 first — the Node track is self-contained and doesn't assume you've done the
Python projects; 21-22 assume nothing except general backend comfort either, though
they're calibrated above intern/new-grad OA difficulty by design.

## Node/Express track (Projects 16-20)

Stack: Node.js 22, TypeScript (compiled via `ts-jest`, not a separate build step), Express
4, Jest + Supertest. No database server or native-compiled dependencies are required —
persistence is an in-memory repository abstraction, the same pattern used throughout the
Python track, so nothing beyond `npm install` is needed to run any of these.

**Environment note:** every project's `package.json` pins `"typescript": "5.9.x"`
deliberately — `ts-jest` is incompatible with the TypeScript 7 compiler API, and a bare
`npm install typescript` on a fresh environment can otherwise resolve to TS7. If you ever
add or reinstall dependencies and tests start failing with an error mentioning `ts-jest`
and "does not expose the JavaScript compiler API," reinstall with the pinned version from
`package.json` rather than upgrading TypeScript.

```
cd projects/16-team-task-board/candidate
npm install
npm test
```

## Black-box full-app debugging tier (Projects 21-22)

Projects 21-22 are structurally different from every other project in this suite, and
you should know how before you start one.

**Every project 1-20 tells you what's broken** (a bug report in the README, a failing
public test, or both). **Projects 21-22 do not.** Each ships a real, working,
minimal frontend (plain HTML/CSS/vanilla JS, no framework, no build step — served by
the same Express app) on top of an unfamiliar backend. Nearly all public tests pass
on the starting code. Your job starts with *using the running application* to find
something that doesn't behave the way it should, before you ever open the source.
Only once you've reproduced a concrete problem does this become a normal debugging
task: trace it, form hypotheses, fix it, and write your own regression test — nobody
hands you one.

This trains a specific, different skill from Projects 1-20: being dropped into an
unfamiliar *product*, not just an unfamiliar *codebase* — observe → reproduce → trace
→ hypothesize → test the hypothesis → identify the underlying invariant → fix →
regression test → verify end-to-end. It's deliberately calibrated slightly above
typical intern/new-grad OA difficulty (8.5-9/10) because the goal here is skill
development, not assessment-difficulty matching.

```
cd projects/21-teamnotes/candidate
npm install
npm run dev
# open http://localhost:3000 in a browser, or curl the API directly
```

Both projects include debug utilities (documented plainly in each README) —
`POST /debug/reset` to restore seed data, and, for Project 22, `POST
/debug/advance-time` to deterministically fast-forward time-based behavior without
waiting. These are normal assessment-environment infrastructure, not spoilers.

## Assessment format (for tooling, not required reading to attempt a project)

Every project also has a root-level `assessment.yaml` — a vendor-neutral manifest
separating **policy** from **enforcement**:

- `SKILL.md` (policy) defines how a compliant AI assistant should *behave*.
- `assessment.yaml` (enforcement) defines what the assessment environment *permits*:
  which paths are candidate-visible, which are blocked, the time limit, and where to
  load the guarded AI instructions from.

This makes it possible for a future runner/CLI to expose only `candidate_access` paths
to an agent's workspace, inject `SKILL.md` as that agent's instructions, keep
`blocked_access` paths physically out of reach, enforce the timebox, run public tests,
and reveal `evaluator_private/` only after submission — with any capable coding agent,
not a specific vendor. No such runner exists yet; the format alone is the deliverable.

## Status

See `GENERATION_STATE.md` (build/validation tracker) for which projects are fully built
and validated. See `PROGRESS.md` (yours) to log your own attempts.

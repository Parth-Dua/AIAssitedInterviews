# Master Evaluator — Private Curriculum Review

Generator-facing. Not part of any candidate-facing content. This is the section-43
"private master evaluator" review of the full 15-project suite.

## 1. Concept coverage

| Concept area (master spec §8) | Where covered |
|---|---|
| Codebase reasoning (read unfamiliar code, trace data/execution) | Every project 1-10, 13, 15 |
| Reproducing issues from tests/logs | 1-10, 13, 15 |
| Hypothesis formation / narrowing scope | All debugging projects; explicit "competing hypotheses" in 8, 9, 10, 15 |
| Root-cause reasoning | All debugging projects |
| Regression testing | All debugging + implementation projects |
| HTTP APIs / request-response models | 1-10, 13, 15 (FastAPI); 11-12 optionally via thin wrapper |
| Validation | 1 (Pydantic), 3, 7 (role validation), 13 (response validation) |
| Business logic / domain modeling | All |
| Database interaction / queries | 2 (SQLAlchemy/SQLite) |
| Pagination / filtering | 5 |
| State & state machines | 4 (aliasing), 8 (state transitions), 10 (async state), 15 (state machine) |
| Error handling | 1, 3, 5, 7, 8, 9, 13, 15 |
| Authorization / ownership | 7 |
| Caching | 6, 13 |
| Async Python | 10, 13 |
| External service calls (fake) | 13 (fake model clients), 9 (fake fulfillment client) |
| Background/worker processing | 9 (webhook→fulfillment), 10 (worker pool), 15 (job platform) |
| Idempotency / duplicate handling | 9 |
| Retries | 9, 13 |
| Concurrency / race conditions | 10 |
| Transaction/consistency reasoning | 8 (save-then-mutate ordering), 14 (DB constraint discussion) |
| Testing (pytest, unit/integration/API, mocking via fakes) | All |
| LLD: interfaces, composition, extensibility | 11, 12 |
| HLD: requirements, APIs, schema, scaling, caching, failure handling, tradeoffs | 14 |
| AI-engineering-flavored backend (fake deterministic models) | 13 |

No concept was included solely for "production education" — each was checked against
the rule-46 question during design (see each project's `bug_design.md` /
`EVALUATOR.md` "Anything included for production-education rather than signal?"
line, always answered "No" with a specific justification).

## 2. Interview-format coverage (master spec §5)

- **A. AI-Assisted Debugging Assessment:** Projects 1, 2, 3, 4, 9, 10 (pure debugging,
  no feature).
- **B. Debugging + Feature Implementation:** Projects 5, 6, 7, 8, 13, 15.
- **C. Existing-code implementation task:** feature portions of 5, 6, 7, 8, 13
  (pagination/filtering, TTL cache, new role, new discount type, response validation).
- **D. Low-Level Design:** Projects 11, 12.
- **E. High-Level Design:** Project 14.

Every format from the master spec is represented at least twice except HLD (once, as
directed — "use sparingly").

## 3. Difficulty curve

| Tier | Projects | Target | Achieved (stated in each README) |
|---|---|---|---|
| Fundamentals | 1-4 | 5-6/10, 45-60m | 5, 5, 6, 6 — 45-60m each |
| Harder debugging + modification | 5-8 | 6-7/10, 60-75m | 6, 7, 7, 7 — 60-75m each |
| Advanced debugging | 9-10 | 7-8/10, 60-90m | 8, 8 — 60-90m each |
| LLD | 11-12 | 7-8/10, 60-90m | 7, 8 — 60-90m each |
| AI-engineering | 13 | 7-8/10, 75-90m | 8 — 85m |
| HLD | 14 | realistic for level, 45-60m | 6, 45-60m |
| Final capstone | 15 | 8-9/10, 75-90m | 9 — 75-90m |

Monotonic difficulty increase within the debugging track (1→4→5→8→9→10→15), with LLD
(11-12), AI-eng (13), and HLD (14) interleaved at comparable difficulty to their
neighbors rather than restarting the curve. No project reaches a "10/10 puzzle" — the
hardest (15) is scoped as one invariant applied across three call sites, not a
multi-incident scenario.

## 4. Duplicate-skill / cross-project diversity analysis (master spec §39)

**Domains used (no repeats):** e-commerce pricing (1), library loans (2), user
profile settings (3), support tickets (4), warehouse inventory (5), notification
preferences (6), team workspace docs (7), promo coupons (8), payment webhooks (9),
async batch jobs (10), API rate limiting (11, LLD), feature flags (12, LLD), LLM
inference routing (13), interview scheduling (14, HLD — also this curriculum's own
domain, used deliberately as a familiar, self-referential choice), data-export job
platform (15). Fifteen distinct domains, zero repeats.

**Bug-mechanism diversity (the thing most at risk of repetition across 15 bug-based
projects):**

| # | Mechanism | Distinguishing feature |
|---|---|---|
| 1 | Wrong variable used in a comparison (post- vs. pre-discount subtotal) | Simple variable mixup |
| 2 | SQL/ORM query ignores a relevant column (`renewed_due_at`) | Query-filter incompleteness |
| 3 | `model_dump()` without `exclude_unset` | Library-semantics gotcha (serialization) |
| 4 | Mutable default argument + in-place mutation | Object aliasing / shared state |
| 5 | Off-by-one cursor boundary (`>=` vs `>`) | Pagination boundary logic |
| 6 | Cache never invalidated/updated on write | Cache-consistency (write path) |
| 7 | Authorization check unscoped to the right tenant/resource | AuthZ scoping |
| 8 | Mutation after a defensive-copy `save()` | Call-order / copy-semantics interaction |
| 9 | Idempotency check exists but is never invoked | Dead-code / unused-safety-mechanism |
| 10 | Lost update from an `await` inside a check-then-act critical section | True async race condition |
| 13 | Cache write policy doesn't distinguish response provenance | Cache-consistency (a DIFFERENT angle from 6: what to cache, not when to invalidate) |
| 15 | Boolean guard logically only covers one of several invalid states | Boolean-logic error in a state guard |

Every mechanism is structurally distinct. The two cache bugs (6, 13) were deliberately
built around different failure angles (invalidation-on-write vs. provenance-based
write policy) per master-spec §39's explicit example. The two "unused correct
safety mechanism" bugs (7's unscoped-vs-scoped lookup, 9's unused `has_seen`) are the
closest pair in shape, but operate in different domains (authz vs. idempotency) and
were each independently solver-simulated and found appropriately challenging.

**Tempting-but-incomplete-fix diversity:** capped-discount (1), `exclude_none`
(3), half-fixed None-sentinel-but-still-mutates-caller (4), filter-after-paginate
(5), cache-the-request-not-the-persisted-value (6), owner_id-only overcorrection (7),
order-status-gate instead of event_id (9), per-call-new-lock (10), unclamped
fixed_amount (8), no-caching overcorrection (13), unconditional-cancel (15),
isinstance-branching (11, 12 — same shape, but this is the canonical LLD
polymorphism trap and appearing in both of the suite's two LLD projects is
intentional, not accidental repetition, since it's the one thing every LLD
follow-up requirement is designed to test). No two debugging projects share a trap
mechanism.

**Repository architecture variation:** api/services/repositories (1, 3, 5, 6, 7, 8,
9, 15) with domain/ added where a plain Python object matters (4, 8); api/db/models
split with SQLAlchemy (2); services/clients/cache split (13); services/workers split
(10, 15); plain-package-no-app/ for the two LLD projects (11, 12); no code skeleton
at all for the HLD project (14). Not the same three-folder shape 15 times.

## 5. Solver-simulation results (rule 34, projects 4-15)

All 12 required simulations were run as genuinely isolated agents (candidate repo +
README + SKILL.md only, no bug design/hidden tests/reference solution). Every one
correctly solved its project. Six simulations surfaced a real leakage or
difficulty-calibration issue that was fixed and re-validated before finalizing:

| Project | Finding | Fix |
|---|---|---|
| 5 | TODO comment named the exact missing wiring | Comment removed |
| 6 | TODO comment prescribed the exact TTL method signature | Comment trimmed |
| 7 | — (clean) | none |
| 8 | Repository docstring described the bug's mechanism | Docstring trimmed |
| 9 | Method docstring stated the diagnostic conclusion outright, dropping effective difficulty from 8/10 to ~4-5/10 | Docstring trimmed |
| 10 | — (clean, and independently reconfirmed full determinism) | none |
| 11 | README explicitly instructed against the anti-pattern (isinstance branching) | Instruction removed, kept only the behavioral requirement |
| 12 | Two README passages over-explained the intended design/refactor | Both trimmed to behavioral requirements only |
| 13 | Class + exception docstrings restated the README's policy next to the buggy code | Both trimmed |
| 14 | — (clean) | none |
| 15 | Pending at time of writing this section — see `GENERATION_STATE.md` for final status | — |

This 6-of-11-completed-so-far leakage rate is the expected, useful output of rule 34
— the process is designed to catch exactly this class of problem, and every finding
was addressed before the project was considered final. Projects 1-3 were calibrated
manually by the generator (establishing the template) rather than via isolated
solver simulation, consistent with `GENERATION_STATE.md`'s documented decision.

## 6. AI-skill audits and agent-independence

Every project's `ai_skill_audit.md` includes: a leakage audit of its `SKILL.md`, an
~8-row table of simulated candidate prompts against expected compliant-assistant
behavior, and a 5-point "Agent portability audit" (added mid-generation, retrofitted
onto Projects 1-3, present from the start in 4-15) confirming: solvable without a
specific vendor; guarded instructions make sense for any capable agent; scoring is
model-independent; no proprietary feature is required; a future runner could swap
providers without changing the problem. Every `SKILL.md` across the suite is
Project 1's text verbatim except each project's final "Scope of this exercise"
paragraph — this was a deliberate design choice (see `CURRICULUM.md`'s assessment.yaml
section) to guarantee the escalating-assistance-levels policy itself never drifts or
accidentally leaks between projects, since it's one audited, reused document rather
than fifteen independently-drafted ones.

Every `assessment.yaml` separates policy (`SKILL.md`) from enforcement
(`candidate_access`/`blocked_access`), so a future runner could mount only
`candidate/` into an arbitrary agent's workspace and inject `SKILL.md` as that
agent's instructions, with no code in this repo assuming a specific vendor.

## 7. Which projects best simulate which real interview format

- **OA (take-home, less proctor interaction):** 1, 2, 3, 5, 6 — self-contained,
  clear pass/fail signal, moderate time.
- **Live debugging interview (interviewer present, back-and-forth):** 4, 9, 10 — the
  reasoning-to-verbalize ratio is high; DEBRIEF.md questions are designed to be asked
  live.
- **Code modification / ticket-style interview:** 5, 6, 7, 8, 13 — "here's a real
  ticket: fix X, add Y."
- **LLD round:** 11, 12.
- **HLD round:** 14.
- **AI-engineering interview with SWE signal:** 13.
- **Final/onsite capstone round:** 15.

## 8. Realism concerns and remaining weaknesses (honest accounting)

- **Solver-simulation time estimates consistently ran shorter than the stated human
  timebox** (e.g., 15-70 minutes vs. stated 45-90 minute windows). This is expected —
  a capable AI agent reads and greps code far faster than a human candidate reasoning
  under interview pressure without full codebase familiarity — and is not itself
  evidence a project is too easy; the timeboxes were calibrated for humans, not
  verified against them (no human pilot testing was possible in this generation
  process). This is the single biggest residual uncertainty in the suite: real human
  timing has not been observed, only inferred from bug complexity and comparison
  across projects.
- **Project 15's fresh solver simulation was still in progress at authoring time**
  for this section; see `GENERATION_STATE.md`/`GENERATION_REPORT.md` for its final
  outcome.
- **Environment quirk (not a curriculum defect):** in some sandboxes, a stray
  `pytest` executable on `PATH` resolves to a different Python environment than the
  one dependencies were installed into, producing a misleading
  `ModuleNotFoundError`. Documented once in root `CURRICULUM.md` rather than
  repeated per project.
- **No live human-AI-assistant transcript was captured for any project** — the
  AI-usage signal (rule 24, 31) is evaluated from the candidate's resulting diff,
  tests, and explanation, per the master spec's explicit allowance ("do not require
  access to a full AI interaction log"). This is a deliberate design choice, not an
  oversight, but it means the "weak AI usage" examples in each `bug_design.md` are
  evaluator judgment aids, not tested against real transcripts.
- **Statistical tests (Project 12's rollout-uniformity checks) use generous
  tolerances specifically to avoid flakiness** — verified deterministic (SHA-256
  based, not process-hash-seeded) and re-run multiple times during validation, but
  this class of test is inherently a slightly softer signal than an exact-equality
  test.
- **The two LLD projects share one trap shape (isinstance-branching)** — flagged
  above in §4 as intentional (it's the canonical LLD extensibility trap), but
  reviewers should not expect a THIRD distinct trap shape if this curriculum is ever
  extended with a third LLD project; a new one would need a genuinely different
  extensibility mechanism to avoid real repetition.

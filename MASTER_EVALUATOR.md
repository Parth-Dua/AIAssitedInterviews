# Master Evaluator — Private Curriculum Review

Generator-facing. Not part of any candidate-facing content. This is the section-43
"private master evaluator" review of the full curriculum: originally a 15-project
Python/FastAPI suite (§1-8 below), extended by user request with a 5-project
Node.js/TypeScript/Express track calibrated to Amazon-style repo-debugging OAs
(§9-10), and further extended with a 2-project black-box full-app debugging tier
(tracked separately once complete — see `GENERATION_STATE.md`). Sections 1-8 describe
the original 15-project suite and are left as originally written except where noted;
sections 9+ cover what changed and was added.

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
| 15 | — (clean; solver independently generalized the fix beyond the reference solution and volunteered the same "transition table" design observation `bug_design.md` notes as a stretch goal) | none |

This 6-of-12 leakage rate is the expected, useful output of rule 34
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
- **Process integrity note:** during finalization, a timing race briefly caused a
  background solver-simulation agent's in-progress fix to Project 15 to be captured
  by an unrelated documentation commit. This was caught during a final full-suite
  test sweep (an unexpected jump from 11 to 20 tests) before publication, and
  corrected by restoring `candidate/` from the correct prior commit — verified
  against a full re-run of all 15 projects' test suites, confirming no other project
  was similarly affected. Documented here and in `GENERATION_STATE.md` for
  transparency rather than omitted.
- **The two LLD projects share one trap shape (isinstance-branching)** — flagged
  above in §4 as intentional (it's the canonical LLD extensibility trap), but
  reviewers should not expect a THIRD distinct trap shape if this curriculum is ever
  extended with a third LLD project; a new one would need a genuinely different
  extensibility mechanism to avoid real repetition.

## 9. Node/Express track (Projects 16-20) — coverage and calibration

Added by explicit user request as a purpose-built Amazon-style repo-based debugging OA
practice track, NOT generic Node.js instruction. Structural conventions from §1-8 carry
over unchanged (candidate/evaluator_private split, SKILL.md as vendor-neutral policy,
assessment.yaml as vendor-neutral enforcement, the same validation loop, fresh solver
simulation for every project).

**Node/Express skill coverage:** Express routing (16-20), middleware ordering and
error-handling middleware (17, 20), async/await and Promise-rejection propagation (17),
validation (16, 20), request context/`req.user` (20), authorization at the resource
level vs. the role level (20), service-layer logic (16-20), in-memory persistence and
query/uniqueness logic (16, 18), pagination — cursor vs. offset (18), caching and
composite-key construction (19), external-client abstraction with a fake/deterministic
client (19), API contract preservation (16, 17, 20), testing with Jest/ts-jest/Supertest
(16-20), mocking/fakes (17, 19), regression tests (16-20). Deliberately NOT covered:
obscure Express internals, JS coercion trivia, event-loop trivia, advanced TypeScript
generics, library-specific hacks — per the master brief's explicit "do not test
framework trivia" constraint (§6 of that brief).

**Amazon-style OA coverage:** all 5 projects are unfamiliar-repository, bounded-codebase,
terminal-testable exercises with a candidate-facing bug report, existing tests,
multi-file reasoning, a strict timebox, guarded AI assistance, and hidden evaluator
tests — the exact shape described in the brief's §2 calibration requirements. Project 17
specifically targets the single most common real Express interview/code-review
topic (async handlers and unhandled promise rejection). Project 20 specifically targets
coarse-role-vs-resource-level authorization, one of the most common real backend
vulnerability classes and interview topics.

**Difficulty progression (independent of the Python track's numbering):** 16 (6/10) →
17 (7/10) → 18 (7/10) → 19 (8/10) → 20 (8.5/10), mirroring the shape of the Python
1→15 progression at a compressed scale — fundamentals, then harder debugging, then
advanced, then a generalizing capstone — as explicitly requested.

**Comparison with the Python track / cross-language skill overlap:** the two tracks
deliberately share *skill categories* (debugging process, root-cause reasoning,
multi-file reasoning, tempting-but-incomplete fixes, hidden-test-carried signal) while
using *different concrete bug mechanisms* in every case, so neither track is a port of
the other:

| Python project | Node project | Shared skill category | Why the mechanism differs |
|---|---|---|---|
| 3 (`exclude_unset`/`exclude_none`) | 16 (merge-order hardcode) | Partial-update (PATCH) semantics | Python: a library-serialization gotcha. Node: a leftover hardcoded business-rule override — no library-specific knowledge needed either way. |
| 6, 13 (cache invalidation-on-write; cache-by-provenance) | 19 (cache key missing a dimension) | Cache correctness | All three are structurally distinct cache-bug angles (see §4's mechanism table); 19 adds a NEW angle (key-construction completeness) not covered by 6 or 13. |
| 5 (cursor boundary off-by-one) | 18 (offset-vs-cursor architecture choice) | Pagination | Python 5's bug is a boundary-comparison logic error in an EXISTING cursor design; Node 18's bug is choosing the WRONG pagination architecture (index-based) from scratch — a design decision, not a boundary slip. |
| 7 (unscoped repository query) | 20 (missing resource-level check atop a correct role gate) | Authorization scoping | Python 7's bug is "used the wrong lookup method, the right one existed unused nearby." Node 20's bug is "no per-resource check exists at all — the middleware's role check is correct but insufficient by construction," a different, complementary lesson about layering coarse and fine-grained authorization. |
| 15 (boolean-logic guard covers one of several invalid states) | 20 (missing check entirely, generalization tested via delegation) | "Does the fix generalize beyond the one reported case" (both capstones) | Python 15 tests whether a candidate notices a LOGIC ERROR generalizes across sibling methods (start/finish/cancel all need the same guard). Node 20 tests whether a candidate's fix generalizes across a NEW FEATURE (delegation) that the fix must recognize, not just across sibling methods. |

No Python project and no Node project share both domain AND bug mechanism; every
"same skill category" pair above uses a genuinely different mechanism, satisfying the
master brief's diversity requirement (§18 of that brief) at the whole-suite level, not
just within the 5 new projects.

## 10. Node track solver-simulation and leakage findings

All 5 required simulations (Projects 16-20) were run as genuinely isolated agents.
Every one correctly solved its project. Three surfaced findings, all fixed and
re-validated:

| Project | Finding | Fix |
|---|---|---|
| 16 | Shared SKILL.md template's body text (not just the scope paragraph) still referenced "Python, FastAPI, Pydantic" from its Python-track origin; README overstated the failing-test count | Genericized the two body-text mentions (making the base template byte-for-byte reusable across both tracks, not just within one); corrected the README's test count |
| 17 | Built concurrently with Project 16's fix, so it inherited the stale (un-genericized) SKILL.md | Applied the same genericization, confirmed via grep |
| 18 | Two code docstrings (on the `sequence` field and the repository class) stated the intended pagination design (cursor-over-offset) and its rationale outright, pre-answering the specific judgment the README asks the candidate to demonstrate | Trimmed both to mechanical facts only, removing the design-rationale sentences; confirmed the README's naming of "cursor-based pagination" as the *required feature* (not the reasoning for it) was correctly left intact, since that's the task specification, not a spoiler |
| 19 | No candidate-facing finding — a nudge toward the collision-safety consideration existed only in the *simulation's own instructions* (a deliberate probe), not in the real README/SKILL.md (confirmed via grep) | None needed; recorded as a methodology note |
| 20 | No leakage found; solver correctly avoided the delegation-wiring trap and fixed both approve/reject without prompting | None needed |

This 3-of-5 finding rate is consistent with the Python track's 6-of-12 rate and
reflects the same intended process value: rule 34 exists to catch exactly this class
of problem before a project is considered final, and every finding here was addressed
before commit.

## 11. Node track agent-independence and AI-skill audit status

Complete for all 5 projects, same structure as §6 of this document. Every
`ai_skill_audit.md` includes the leakage audit, the ~8-row simulated-prompt table, and
the 5-point "Agent portability audit." No project assumes a specific AI vendor, IDE,
or agent framework — `SKILL.md` remains pure behavioral policy text, injectable into
any capable assistant exactly as described in `CURRICULUM.md`'s "Assessment format"
section.

## 12. Toolchain reliability note (Node track)

`ts-jest` is incompatible with TypeScript 7's compiler API; a bare `npm install
typescript` in a fresh environment can resolve to TS7 and silently break every test
run with a confusing error. This was discovered and fixed BEFORE any project was
built (verified via a throwaway toolchain test), by pinning `"typescript": "5.9.3"`
in every project's `package.json`. Every project's fresh-install validation (a clean
`rm -rf node_modules && npm install && npm test`, not just the builder agent's own
install) confirmed this pin is sufficient and the toolchain is fully reproducible.
This is documented once in root `CURRICULUM.md` rather than repeated per project,
mirroring how the Python track's `pytest`-vs-`python3 -m pytest` environment quirk was
handled.

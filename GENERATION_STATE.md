# Generation State (private, generator-facing)

Tracks build/validation progress across the growing project suite (originally 15
Python projects; extended to 20 with a Node/Express track; extended again to 22 with
a black-box full-app debugging tier). Not part of any candidate-facing content.

Loop per project: DESIGN → IMPLEMENT CORRECT VERSION → TEST → CREATE CANDIDATE VERSION →
REPRODUCE FAILURE → BUILD HIDDEN TESTS → BUILD REFERENCE SOLUTION → VALIDATE REFERENCE
SOLUTION → SOLVER SIMULATION (projects 4+) → AI-SKILL AUDIT → INTERVIEW-REALISM AUDIT →
REVISE → FINALIZE.

## Python track (Projects 1-15) — complete

| # | Slug | Design | Candidate built | Public tests behave as intended | Hidden tests + ref solution validated | SKILL.md leakage audit | Solver sim | Realism audit | Committed |
|---|------|--------|------------------|----------------------------------|-----------------------------------------|--------------------------|------------|----------------|-----------|
| 1 | orderflow-pricing | done | done | done (8 pass/1 fail as designed) | done (17/17 pass; tempting fix fails 3) | done (no leakage) | n/a (calibration project, done manually) | done | done |
| 2 | library-loan-tracker | done | done | done (7 pass/1 fail as designed) | done (13/13 pass; tempting fix fails 1) | done (no leakage) | n/a (calibration project, informal) | done | |
| 3 | profile-settings-api | done | done | done (1 fail/7 pass) | done (13/13 pass; exclude_none fix fails 1) | done (no leakage) | n/a (calibration project, informal) | done | done |
| 4 | support-ticket-queue | done | done | done (2 fail/6 pass, deterministic) | done (12/12 pass; half-fix fails 1) | done (no leakage) | done (correctly solved, ~15-25min, no leakage found, no out-of-scope access) | done | done |
| 5 | inventory-reservations | done | done | done (3 fail/5 pass) | done (12/12 pass; filter-after-paginate fails 2) | done (no leakage) | done (solved correctly; found+fixed a spoiler TODO comment) | done | done |
| 6 | notification-prefs-cache | done | done | done (2 fail/12 pass) | done (19/19 pass; cache-request-body fix fails 1) | done (no leakage) | done (solved correctly; found+fixed a spoiler TODO in cache.py docstring) | done | done |
| 7 | team-workspace-permissions | done | done | done (3 fail/10 pass) | done (18/18 pass; overcorrection fails 4) | done (no leakage) | done (solved correctly, ~35-50min, no leakage, no out-of-scope access) | done | done |
| 8 | coupon-redemption | done | done | done (6 fail/8 pass) | done (18/18 pass; unclamped fixed_amount fails 1) | done (no leakage) | done (solved correctly; found+fixed a near-spoiler docstring) | done | done |
| 9 | payment-webhook-handler | done | done | done (1 fail/8 pass) | done (13/13 pass; order-status-gate fails 3-4) | done (no leakage) | done (solved correctly; found+fixed a docstring that gave away the diagnosis) | done | done |
| 10 | async-job-worker-pool | done | done | done (1 fail/5 pass, deterministic across 3+ runs) | done (9/9 pass; per-call-lock fails 3-4) | done (no leakage) | done (solved correctly, ~30-60min, fully deterministic, no leakage) | done | done |
| 11 | rate-limiter-lld | done | done | done (10/10 fail as expected, NotImplementedError) | done (19/19 pass; isinstance-branching fails 3) | done (no leakage) | done (solved correctly, polymorphic design, no rewrite needed; found+fixed over-explicit README hint) | done | done |
| 12 | feature-flag-engine-lld | done | done | done (10/10 fail as expected) | done (18/18 pass; isinstance-branching fails 4, hardcoded-order fails 1) | done (no leakage) | done (solved correctly, polymorphic; found+fixed 2 over-explicit README hints) | done | done |
| 13 | llm-request-router | done | done | done (2 fail/6 pass) | done (12/12 pass; no-caching overcorrection fails 2) | done (no leakage) | done (solved correctly; found+fixed two docstring spoilers) | done | done |
| 14 | interview-scheduling-hld | done | done | n/a (design deliverable; bonus algo 4/4 fail as expected) | done (bonus 12/12 pass incl. hidden) | done (no leakage) | done (strong design produced, ~45-60min, no leakage, no over-engineering) | done | done |
| 15 | job-processing-platform-final | done | done | done (2 fail/9 pass) | done (20/20 pass; unconditional-cancel fails 8) | done (no leakage found) | done (solved correctly, generalized fix independently, ~60-80min, no leakage) | done | done |

## Node/Express track (Projects 16-20) — complete

Amazon-style repo-based debugging OA calibration. TypeScript 5.9.3 (pinned for ts-jest
compatibility) + Express 4 + Jest + Supertest. Same validation loop as the Python track.

| # | Slug | Design | Candidate built | Public tests behave as intended | Hidden tests + ref solution validated | SKILL.md leakage audit | Solver sim | Realism audit | Committed |
|---|------|--------|------------------|----------------------------------|-----------------------------------------|--------------------------|------------|----------------|-----------|
| 16 | team-task-board | done | done | done (2 fail/10 pass) | done (16/16 pass; hardcode-removed-no-validation fix fails 1) | done (no leakage; genericized shared SKILL.md body for cross-track reuse) | done (solved correctly, ~15-25min; found+fixed leftover Python references in SKILL.md and a README test-count error) | done | done |
| 17 | order-notification-service | done | done | done (1 fail/7 pass, deterministic across 3+ runs) | done (11/11 pass; direct-res.send bypass fails 3) | done (no leakage) | done (solved correctly, ~30-50min; found+fixed inherited SKILL.md leftover) | done | done |
| 18 | shared-playlist-api | done | done | done (6 fail/10 pass) | done (20/20 pass; offset-slicing fails 1 hidden) | done (no leakage) | done (solved correctly, ~35-50min; found+fixed pagination-design spoiler comments) | done | done |
| 19 | product-price-lookup | done | done | done (2 fail/10 pass) | done (17/17 pass; delimiter-less key fails 2) | done (no leakage) | done (solved correctly, ~30-50min; no candidate-facing revision needed) | done | done |
| 20 | expense-approval-platform | done | done | done (4 fail/15 pass) | done (27/27 pass; delegation-has-no-effect fails 2) | done (no leakage) | done (solved correctly, both approve+reject fixed, delegation trap avoided, ~45-70min, no leakage) | done | done |

## Black-box full-app debugging tier (Projects 21-22) — in progress

New tier added after the 20-project suite. Minimal static HTML/JS frontend served by
Express + the same TypeScript/Express/Jest/Supertest backend toolchain. README does NOT
reveal the bug; candidate discovers it via application usage. Public tests pass on the
buggy starting state (no red test announces the bug); the candidate is expected to write
their own regression test after discovering the problem.

| # | Slug | Design | Candidate built | Public tests behave as intended | Hidden tests + ref solution validated | SKILL.md leakage audit | Solver sim | Realism audit | Committed |
|---|------|--------|------------------|----------------------------------|-----------------------------------------|--------------------------|------------|----------------|-----------|
| 21 | teamnotes | done | done | done (21/21 pass on buggy state — discovery-through-usage design confirmed) | done (26/26 pass; tags-merge-only tempting fix fails on lost-content-update hidden test) | done (no leakage) | done (discovered primarily via usage not code-reading, ~50-75min, reliable/deterministic repro; found+fixed 2 frontend spoiler comments) | done | done |
| 22 | neighborhood-marketplace | done | pending | | | | | | |

## Notes / decisions

- Projects 1-3 solver-simulated informally by the generator during calibration (rule 34
  requires fresh-solver simulation for projects 4-15; 1-3 establish the baseline format).
- Scope calibrated to the lower-middle of the LOC guidance in the master prompt to keep
  15 full, working, validated projects tractable — semantic complexity prioritized over
  line count per rule 10.
- **Mid-generation update (applied starting Project 1 retrofit, standard for all
  subsequent projects):** every project gets a root-level `assessment.yaml` (vendor
  neutral: `assessment.title/type/time_limit_minutes`, `ai.mode: guarded` +
  `ai.instructions` pointing at the project's SKILL.md, `candidate_access` listing the
  `candidate/**` paths, `blocked_access: ["evaluator_private/**"]`, adapted per project's
  actual layout). `ai_skill_audit.md` for every project gets an added "Agent portability
  audit" section (5-point checklist: solvable without Claude specifically; guarded
  instructions make sense for any capable agent; scoring is model-independent; no
  proprietary/vendor-specific feature required; a future runner could swap providers
  without changing the problem). Project 1 retrofitted. Projects built after this point
  include both from the start.
- **Process note:** a background solver-simulation agent's in-progress fix to Project
  15's candidate/ was briefly captured by an unrelated `git add -A && git commit`
  (the "Add MASTER_EVALUATOR.md..." commit) due to a timing race — caught during
  final verification (test count jumped from 11 to 20 unexpectedly) and corrected by
  restoring `candidate/` from the prior correct commit before finalizing. No other
  project was affected (this was checked for specifically). This class of race was
  otherwise avoided throughout generation by always checking `git status`/rerunning
  `pytest` immediately before every commit and treating any unexpected diff as a
  signal to check for a live background agent first.
- **Node track addition (Projects 16-20):** user-requested extension, same conventions
  preserved (candidate/evaluator_private split, assessment.yaml, SKILL.md, solver
  simulation, quality gates). Toolchain choice: TypeScript over plain JS (master brief's
  preference), with `typescript` deliberately pinned to `5.9.3` in every project's
  `package.json` — a fresh `npm install typescript` can resolve to TypeScript 7, which
  `ts-jest` cannot use (confirmed by direct testing before building). Persistence is
  in-memory (no database/native deps), matching the Python track's approach and keeping
  every project a pure `npm install && npm test` with no external services.
  `node_modules/`/`dist/` added to the repo `.gitignore`. Project 16's SKILL.md was
  genericized after its solver simulation flagged leftover "Python, FastAPI, Pydantic"
  wording inherited from the shared template — Projects 18-20 correctly copied the fixed
  version from the start; Project 17 (built concurrently with the fix) inherited the
  stale version and needed the same correction applied after its own solver sim.
- **Black-box tier addition (Projects 21-22):** a second user-requested extension,
  structurally different from every prior project — no failing public test announces
  the bug; the README does not name it; a minimal static HTML/CSS/vanilla-JS frontend
  (served by the same Express app via `express.static`, no build tooling) is the
  discovery surface. Same underlying TypeScript/Express/Jest toolchain and
  candidate/evaluator_private convention otherwise.

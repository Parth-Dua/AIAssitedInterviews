# Generation State (private, generator-facing)

Tracks build/validation progress across the 15-project suite. Not part of any
candidate-facing content. Safe to delete once GENERATION_REPORT.md is finalized, but
kept during the build for resumability.

Loop per project: DESIGN → IMPLEMENT CORRECT VERSION → TEST → CREATE CANDIDATE VERSION →
REPRODUCE FAILURE → BUILD HIDDEN TESTS → BUILD REFERENCE SOLUTION → VALIDATE REFERENCE
SOLUTION → SOLVER SIMULATION (projects 4-15) → AI-SKILL AUDIT → INTERVIEW-REALISM AUDIT →
REVISE → FINALIZE.

| # | Slug | Design | Candidate built | Public tests behave as intended | Hidden tests + ref solution validated | SKILL.md leakage audit | Solver sim | Realism audit | Committed |
|---|------|--------|------------------|----------------------------------|-----------------------------------------|--------------------------|------------|----------------|-----------|
| 1 | orderflow-pricing | done | done | done (8 pass/1 fail as designed) | done (17/17 pass; tempting fix fails 3) | done (no leakage) | n/a (calibration project, done manually) | done | done |
| 2 | library-loan-tracker | done | done | done (7 pass/1 fail as designed) | done (13/13 pass; tempting fix fails 1) | done (no leakage) | n/a (calibration project, informal) | done | |
| 3 | profile-settings-api | pending | | | | | n/a | | |
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
| 15 | job-processing-platform-final | done | done | done (2 fail/9 pass) | done (20/20 pass; unconditional-cancel fails 8) | done (no leakage found; mechanical docstrings from the start) | in progress | pending | done |

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

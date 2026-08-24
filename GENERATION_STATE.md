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
| 2 | library-loan-tracker | pending | | | | | n/a | | |
| 3 | profile-settings-api | pending | | | | | n/a | | |
| 4 | support-ticket-queue | pending | | | | | | | |
| 5 | inventory-reservations | pending | | | | | | | |
| 6 | notification-prefs-cache | pending | | | | | | | |
| 7 | team-workspace-permissions | pending | | | | | | | |
| 8 | coupon-redemption | pending | | | | | | | |
| 9 | payment-webhook-handler | pending | | | | | | | |
| 10 | async-job-worker-pool | pending | | | | | | | |
| 11 | rate-limiter-lld | pending | | | | | | | |
| 12 | feature-flag-engine-lld | pending | | | | | | | |
| 13 | llm-request-router | pending | | | | | | | |
| 14 | interview-scheduling-hld | pending | | | | | | | |
| 15 | job-processing-platform-final | pending | | | | | | | |

## Notes / decisions

- Projects 1-3 solver-simulated informally by the generator during calibration (rule 34
  requires fresh-solver simulation for projects 4-15; 1-3 establish the baseline format).
- Scope calibrated to the lower-middle of the LOC guidance in the master prompt to keep
  15 full, working, validated projects tractable — semantic complexity prioritized over
  line count per rule 10.

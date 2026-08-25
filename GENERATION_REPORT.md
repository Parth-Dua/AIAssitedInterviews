# Generation Report

## Total projects
22 of 22 built and validated: the original 15-project Python/FastAPI suite (Projects
1-15); a 5-project Node.js/TypeScript/Express track (Projects 16-20) added by a
subsequent user request, calibrated to Amazon-style repo-based debugging OAs; and a
2-project black-box full-app debugging tier (Projects 21-22) added by a further user
request — structurally distinct from every other project (real minimal frontend, no
README bug report, discovery through application usage), deliberately calibrated
above typical intern/new-grad OA difficulty (8.5-9/10) for skill development.

## Validation status
Every project passed the full autonomous quality loop (design → implement correct
version → test → create candidate version → reproduce failure/incomplete-state →
build hidden tests → build reference solution → validate reference solution →
solver simulation → AI-skill audit → interview-realism audit → revise → finalize).

For every debugging/implementation project (1-10, 13, 15): the buggy/incomplete
candidate state was verified to produce exactly the intended public-test pass/fail
split; a full reference solution was verified to pass 100% of public + hidden tests;
at least one "tempting but incomplete/wrong" fix was implemented and verified to fail
specific hidden tests while still passing the public suite (or, in several cases,
also failing a public test — documented per project); the candidate repository was
restored to its original starting state and re-verified after every validation pass.

For the two LLD projects (11, 12): the unimplemented starting state was verified to
fail every test with `NotImplementedError`; the reference solution was verified to
pass all public + hidden tests; an isinstance-branching (non-polymorphic) alternative
implementation was verified to fail exactly the hidden test(s) built to catch it.

For the HLD project (14): the main design deliverable has no pytest suite by design
(graded via rubric/discussion, per the master spec) and was instead validated via
fresh-solver design-quality review; its small optional bonus algorithm followed the
same stub/reference/hidden-test validation as the LLD projects.

For the Node/Express track (16-20): the same validation loop as Projects 1-10/13/15
applied one-for-one, on a `npm install && npm test` toolchain (Jest + ts-jest +
Supertest) instead of pytest. Every buggy/incomplete candidate state was verified to
produce the intended pass/fail split on a *fresh* `npm install` (not just the builder
agent's own install), confirming the pinned-TypeScript toolchain is reproducible; every
reference solution passed 100% of public + hidden tests; every tempting-but-incomplete
fix was verified to fail its targeted hidden test(s) while passing the public suite (or,
for Project 16, also failing nothing new at the public level, and for Project 18/20,
also passing some public tests it shouldn't have fully "solved" — documented per
project). Project 17's async-hang reproduction was independently re-run 3 times fresh
to confirm determinism (no real timers, no flakiness).

For the black-box tier (21-22): a structurally different validation shape, since the
starting candidate state's public tests are designed to ALL (or nearly all) pass —
the opposite of every other project's validation step. Both were verified to produce
exactly this (21/21 and 25/25 respectively, the latter across 3 fresh-install runs to
confirm determinism given the injectable-clock time-advance mechanism). The bug in
each was independently reproduced by the orchestrator via raw `curl` requests against
a live `npm run dev` server (not just unit tests) before and after applying the
reference fix, confirming the defect is real and observable through the actual
running application, not merely encoded in a test assertion. Both tempting-but-
incomplete fixes were verified to fail their targeted hidden tests while the
candidate-visible public suite kept passing throughout.

See `GENERATION_STATE.md` for the per-project validation matrix and
`MASTER_EVALUATOR.md` for the full private curriculum review (concept coverage,
duplicate-skill analysis, solver-simulation findings, realism audit).

## Project categories

| Category | Projects | Count |
|---|---|---|
| Debugging-heavy (primary) | 1, 2, 3, 4, 9, 10, 15, 16, 17, 19, 21, 22 | 12 |
| Debugging + feature implementation | 5, 6, 7, 8, 13, 18, 20 | 7 |
| Low-level design | 11, 12 | 2 |
| AI-engineering backend | 13 | 1 (also counted above as implementation) |
| High-level design | 14 | 1 |
| Black-box full-app debugging | 21, 22 | 2 (also counted above as debugging-heavy) |

Debugging is the dominant category throughout the suite, consistent with master
spec §2/§4's requirement, and remains dominant after both extensions (12
primarily-debugging projects across all three tiers, plus 15 and 20 each counting as
debugging-heavy final/capstone projects despite including a feature).

## Interview-format coverage
AI-Assisted Debugging Assessment (A): 1, 2, 3, 4, 9, 10, 16, 17, 19.
Debugging + Feature Implementation (B): 5, 6, 7, 8, 13, 15, 18, 20.
Existing-code implementation task (C): feature portions of 5, 6, 7, 8, 13, 18, 20.
Low-Level Design (D): 11, 12.
High-Level Design (E): 14.
Black-Box Full-App Debugging (a sixth format, beyond the original master spec's five,
added per the tier-21-22 request): 21, 22.
All five original formats are represented in both the Python and Node tracks (except
LLD/HLD, deliberately Python-only per the original spec's "use sparingly" guidance
for HLD and the Node track's focus on repo-debugging OA calibration rather than
design rounds).

## Difficulty distribution
Python track: 1-4: 5-6/10 (45-60m). 5-8: 6-7/10 (60-75m). 9-10: 8/10 (60-90m). 11-12:
7-8/10 (60-90m). 13: 8/10 (75-90m). 14: 6/10-equivalent HLD depth (45-60m). 15: 9/10
(75-90m). Monotonic increase through the debugging track; LLD/AI-eng/HLD interleaved
at difficulty comparable to their neighbors.
Node track (independent progression, not a continuation of the Python numbering —
16 is comparable to Python's fundamentals tier): 16: 6/10 (45-60m). 17: 7/10 (45-60m).
18: 7/10 (60-75m). 19: 8/10 (60-75m). 20: 8.5/10 (60-90m).
Black-box tier (deliberately above both other tiers, and above the two other
capstones — 15 and 20 — as the two hardest projects in the curriculum): 21: 8.5-9/10
(90m). 22: 9/10 (105m), the single hardest project in the whole suite.

## Solver simulations performed
19 of 19 required (rule 34, Python projects 4-15 + all of Node projects 16-20 + both
black-box projects 21-22) — see `MASTER_EVALUATOR.md` §5, §10, and §13 for the full
tables. Every simulation correctly solved its project from candidate repo + README +
SKILL.md alone, with no access to evaluator_private/; the two black-box simulations
were additionally instructed not to read source code until after exploring the
running application, and both complied and discovered their bugs primarily through
usage. Eleven surfaced a leakage or difficulty-calibration finding (six in the Python
track, three in the Node track, two in the black-box tier — the black-box tier's
findings were both frontend code comments, a first for this curriculum); each was
fixed and re-validated before the project was finalized. Project 15 (Python capstone),
Project 20 (Node capstone), and Project 22 (black-box capstone, the curriculum's
hardest project) all solved cleanly with no leakage found in their final validated
state, and all three independently generalized their fix beyond the minimum the
reported problem required.

## AI-skill audits performed
22 of 22 (one per project) — leakage audit + simulated-prompt table + agent
portability audit, in every `evaluator_private/ai_skill_audit.md`. The black-box
tier's SKILL.md additionally includes a "Black-box discovery phase" section (guarding
against the assistant naming the bug/location before the candidate has done real
exploration), also audited for leakage.

## Agent-independence audit status
Complete for all 22 projects. Every `SKILL.md` is written as vendor-neutral
behavioral policy (no tool names, no permission-system assumptions, no
vendor-specific mechanics) and is Project 1's text verbatim except each project's
final scope paragraph — including across the stack boundary: Project 16's solver
simulation caught leftover Python/FastAPI/Pydantic wording in the two spots where the
shared template's body text (not just the per-project scope paragraph) mentioned
stack-specific examples; those were genericized so the SAME base SKILL.md text is now
byte-for-byte reusable across both the Python and Node tracks, not just within one.
Every `assessment.yaml` (added mid-generation per an explicit user request,
retrofitted onto Projects 1-3 and present from the start in 4-22) separates policy
(SKILL.md) from enforcement (candidate_access/blocked_access), confirmed workable
with any capable coding agent, not a specific product.

## Mid-generation updates applied
1. A user-requested update introduced `assessment.yaml` as a standardized,
   vendor-neutral assessment-environment manifest per project, and an added
   "Agent portability audit" section in every `ai_skill_audit.md`. This was
   retrofitted onto the already-completed Project 1 and applied to every
   subsequent project from the start.
2. A second user-requested update extended the suite with a 5-project Node.js/
   TypeScript/Express track (Projects 16-20), preserving every established
   convention (candidate/evaluator_private split, SKILL.md, assessment.yaml, the
   validation loop) on a new stack, purpose-built for Amazon-style repo-debugging
   OA practice. Nothing in Projects 1-15 was modified to accommodate this beyond
   adding `node_modules/`/`dist/` to the repo `.gitignore`.
3. A third user-requested update extended the suite with a 2-project black-box
   full-app debugging tier (Projects 21-22), the hardest projects in the
   curriculum, adding a minimal static frontend (served by the same Express app,
   no framework/build step) and shifting the discovery model from "README/test
   names the bug" to "candidate discovers it through application usage." Nothing
   in Projects 1-20 was modified to accommodate this.

See `GENERATION_STATE.md`'s "Notes / decisions" section and `CURRICULUM.md`'s
"Assessment format" / "Node/Express track" / "Black-box full-app debugging tier"
sections for details.

## Known limitations

- Human timing was not empirically verified — all timeboxes are calibrated from bug
  complexity, repository size, and comparison across the suite, not from piloting
  with real candidates. Solver-simulation completion times (by a capable AI agent)
  consistently ran well under the stated human timebox, which is expected and
  doesn't by itself indicate a project is miscalibrated for a human, but it is not
  proof the timebox is correct either.
- No live AI-assistant interaction transcript exists for any project; AI-usage
  judgment is evaluated from the candidate's resulting diff, tests, and explanation,
  per the master spec's explicit allowance for this.
- A repo-wide git-push permission issue (this session's GitHub App does not have
  access to the target repository/org) meant all work was committed locally
  throughout generation and could not be pushed to the remote until that access is
  granted. See the final message in this session for the exact remediation the repo
  owner needs to take.
- The suite has not been reviewed by a human domain expert; it has been reviewed
  only by the generation process's own audits (interview-realism audit,
  AI-trivialization check, solver simulation) as documented per project.
- Two separate timing races during finalization briefly caused a background
  solver-simulation agent's in-progress fix (Project 15, then again around Project
  20's toolchain files) to be captured by an unrelated commit; both were caught and
  corrected before publication via full-suite test sweeps (see `MASTER_EVALUATOR.md`
  §8 and §14 for the full account). A final, independent full-suite sweep across all
  22 projects (fresh `pytest`/`npm install && npm test` for every one, not relying on
  any builder or solver-sim agent's own runs) was performed immediately before this
  report was last finalized, and found no further instances.
- The black-box tier's "discoverability" property (§13 of `MASTER_EVALUATOR.md`) was
  validated by exactly two fresh-solver simulations per project (one for TeamNotes,
  one for Neighborhood Marketplace). This is a smaller validation sample than would
  be ideal for a format this novel to the curriculum; a human pilot (or additional
  independent solver runs) would strengthen confidence further, particularly for
  Project 22 where the solver's own report noted its first reproduction attempt
  initially looked clean due to call-ordering, before it deliberately varied the
  ordering and found the real bug — a sign the discovery signal, while sufficient,
  is not maximally forgiving of a candidate's exploration strategy on a first pass.

## Exact command to begin Project 1 (Python track), Project 16 (Node track), or
## Project 21 (black-box tier)

```bash
# Python track
cd projects/01-orderflow-pricing/candidate
cat README.md
pip install -e ".[dev]"
python3 -m pytest -q

# Node track
cd projects/16-team-task-board/candidate
cat README.md
npm install
npm test

# Black-box tier (start the app and explore it — don't read src/ first)
cd projects/21-teamnotes/candidate
cat README.md
npm install
npm run dev
# open http://localhost:3000
```

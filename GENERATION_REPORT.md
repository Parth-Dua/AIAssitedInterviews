# Generation Report

## Total projects
15 of 15 built and validated.

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

See `GENERATION_STATE.md` for the per-project validation matrix and
`MASTER_EVALUATOR.md` for the full private curriculum review (concept coverage,
duplicate-skill analysis, solver-simulation findings, realism audit).

## Project categories

| Category | Projects | Count |
|---|---|---|
| Debugging-heavy (primary) | 1, 2, 3, 4, 9, 10, 15 | 7 |
| Debugging + feature implementation | 5, 6, 7, 8, 13 | 5 |
| Low-level design | 11, 12 | 2 |
| AI-engineering backend | 13 | 1 (also counted above as implementation) |
| High-level design | 14 | 1 |

Debugging is the dominant category throughout the suite, consistent with master
spec §2/§4's requirement (8 primarily-debugging projects: 1,2,3,4,9,10,15 plus 15's
counting rule that the integrated final counts as debugging-heavy even though it
includes a feature).

## Interview-format coverage
AI-Assisted Debugging Assessment (A): 1, 2, 3, 4, 9, 10.
Debugging + Feature Implementation (B): 5, 6, 7, 8, 13, 15.
Existing-code implementation task (C): feature portions of 5, 6, 7, 8, 13.
Low-Level Design (D): 11, 12.
High-Level Design (E): 14.
All five formats from the master spec are represented.

## Difficulty distribution
1-4: 5-6/10 (45-60m). 5-8: 6-7/10 (60-75m). 9-10: 8/10 (60-90m). 11-12: 7-8/10
(60-90m). 13: 8/10 (75-90m). 14: 6/10-equivalent HLD depth (45-60m). 15: 9/10
(75-90m). Monotonic increase through the debugging track; LLD/AI-eng/HLD
interleaved at difficulty comparable to their neighbors.

## Solver simulations performed
12 of 12 required (rule 34, projects 4-15) — see `MASTER_EVALUATOR.md` §5 for the
full table. Every simulation correctly solved its project from candidate repo +
README + SKILL.md alone, with no access to evaluator_private/. Six surfaced a
leakage or difficulty-calibration finding; each was fixed and re-validated before
the project was finalized.

## AI-skill audits performed
15 of 15 (one per project) — leakage audit + simulated-prompt table + agent
portability audit, in every `evaluator_private/ai_skill_audit.md`.

## Agent-independence audit status
Complete for all 15 projects. Every `SKILL.md` is written as vendor-neutral
behavioral policy (no tool names, no permission-system assumptions, no
vendor-specific mechanics) and is Project 1's text verbatim except each project's
final scope paragraph. Every `assessment.yaml` (added mid-generation per an explicit
user request, retrofitted onto Projects 1-3 and present from the start in 4-15)
separates policy (SKILL.md) from enforcement (candidate_access/blocked_access),
confirmed workable with any capable coding agent, not a specific product.

## Mid-generation update applied
A user-requested update introduced `assessment.yaml` as a standardized,
vendor-neutral assessment-environment manifest per project, and an added
"Agent portability audit" section in every `ai_skill_audit.md`. This was retrofitted
onto the already-completed Project 1 and applied to every subsequent project from
the start. See `GENERATION_STATE.md`'s "Notes / decisions" section and
`CURRICULUM.md`'s "Assessment format" section for details.

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

## Exact command to begin Project 1

```
cd projects/01-orderflow-pricing/candidate
cat README.md
pip install -e ".[dev]"
python3 -m pytest -q
```

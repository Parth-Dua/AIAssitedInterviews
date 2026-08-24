# Scoring Rubric — Project 15 (Capstone, 100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the route→service→repository/domain/worker flow; identified that `finish_job` already has *some* guard (established by the passing "finish a never-started job" test) before concluding it's incomplete rather than absent. |
| Debugging process | 15 | Reproduced the reported bug via the failing test before making changes; explicitly ruled out the worker-determinism and repository-aliasing hypotheses (or gave equivalent reasoning) rather than jumping straight to the fix; didn't shotgun-edit. |
| Root-cause reasoning | 20 | Correctly identifies the exact boolean-logic error in `finish_job`'s guard — that `status != "running" and status == "queued"` only ever evaluates true for `"queued"` — and can walk through why, not just that changing the line made a test pass. |
| Bug-fix correctness | 15 | The duplicate-finish public test passes; the fix rejects finishing from *any* non-`"running"` status (not just `"completed"`); the previously-passing "finish a queued job" behavior still works; `finish_job`'s happy paths are untouched. |
| Feature implementation quality | 15 | `POST /jobs/{id}/cancel` exists, is wired correctly, cancels only from `"queued"`, returns a clear rejection (409-level) otherwise, and a cancelled job is genuinely terminal (start/finish on it are rejected). |
| **Generalization / consistency across start, finish, cancel** | 10 | **Capstone-specific category.** Did the candidate recognize that the same invariant — "only transition from the one valid source status" — needs to be applied to `cancel_job` (not left unguarded, mirroring the original bug's shape) and, ideally, to the pre-existing `start_job` gap too? This is scored independently of bug-fix correctness above: a candidate can get full marks on the literal bug fix and the literal feature request while still writing an unconditional `cancel_job` — this category is where that gets caught. |
| Tests added | 10 | Added at least one regression test beyond the given failing ones (e.g. the `"failed"`-terminal generalization, or explicit cancel-rejection cases), or meaningfully strengthened existing coverage. |
| Communication | 5 | Can clearly state expected vs. actual behavior, the precise boolean-logic root cause, why the fix generalizes, and what they checked to rule out other explanations. |

**Passing bar (strong mid-level+ / senior-adjacent backend signal):** ≥75,
all hidden tests pass, and the candidate can explain both the boolean-logic
root cause and why `cancel_job` needs the same guard without being
prompted.

**Red flags:**
- `cancel_job` implemented with no status guard at all (passes the public
  `test_cancel_queued_job_is_accepted` but fails
  `test_cancel_running_job_is_rejected`,
  `test_cancel_completed_job_is_rejected`,
  `test_cancel_failed_job_is_rejected`, and
  `test_cancel_already_cancelled_job_is_rejected` — see `bug_design.md`).
  This is the single most important red flag for this project: it means
  the candidate fixed the literally-reported bug but did not generalize
  the underlying lesson to a sibling method they wrote themselves, in the
  same session, in the same file.
- Fix only special-cases `job.status == "completed"` in `finish_job`
  (passes the given public test but fails the hidden
  `test_duplicate_finish_after_failed_is_also_rejected`).
- Candidate cannot explain *why* the original boolean condition was wrong
  — only that changing it made the test pass.
- Candidate modifies `Job`, `JobRepository`, or `export_worker.py` when
  none of them needed changes — a sign they didn't correctly rule out
  Hypotheses 1/2 before editing.
- Candidate rewrites large parts of the service "to be safe," including an
  unrequested general state-machine framework — the stretch-goal design
  observation in `bug_design.md` is worth *mentioning* in discussion, not
  worth *building* unprompted for this exercise's timebox.

# Scoring Rubric — Project 21 (100 points)

Unlike the earlier repo-debugging projects in this suite, this rubric
explicitly weights the *discovery process* — noticing incorrect behavior
through actual use of the app — not just the final fix.

| Category | Points | Notes |
|---|---|---|
| Exploratory debugging / recognizing incorrect behavior | 15 | Did the candidate actually use the running app (UI, or direct HTTP calls replaying UI actions) rather than jumping straight to reading source looking for "the bug"? Can they describe what they did and what they observed that first looked wrong? |
| Reproduction quality | 15 | Reduced what they noticed to a minimal, deterministic, repeatable sequence (ideally scriptable via curl/supertest) rather than something that "sometimes happens." Correctly isolates which specific sequence of actions triggers the problem. |
| Hypothesis formation & evidence gathering | 15 | Considered more than one explanation before settling on the real one (e.g., "is the tag write itself unreliable?", "is there a caching/staleness issue on reads?") and ruled them out with actual evidence (a GET immediately after the quick-add, reading the repository for a cache) rather than guessing. |
| Root-cause reasoning | 15 | Correctly identifies that `NoteService.updateNote` never compares `payload.version` to `existing.version`, and can articulate why that specific endpoint (unlike the tag-add endpoint) needed that check in the first place. |
| Fix correctness & scope | 20 | Public tests pass; hidden tests pass — including the lost-content-update test, which specifically catches a fix that only merges tags. The fix rejects (409) rather than partially applies a stale save; a current-version save still succeeds normally; no unrelated behavior changed. |
| Regression tests added | 10 | Candidate added at least one test that actually encodes the discovered bug (not just a general smoke test) — verified by evaluator reverting the candidate's fix and confirming the candidate's test then fails (see `EVALUATOR.md` step 4). |
| Communication / explaining the invariant | 10 | Can state, in their own words, the invariant their fix enforces ("a save should only succeed if the client's view of the note is still current"), and — if they went down the tags-merge-only path first — can explain concretely why it was insufficient. |

**Passing bar (strong new-grad+/mid-level signal):** ≥75, hidden tests
pass, candidate's own regression test independently fails against the
unfixed code, and candidate can explain the invariant without prompting.

**Red flags:**
- Fix passes the tag-loss scenario but fails the lost-content-update hidden
  test (the tags-merge-only incomplete fix — see `bug_design.md`).
- Candidate's added test would also pass against the *original buggy* code
  (i.e., it doesn't actually exercise the bug) — this scores near-zero on
  "regression tests added" regardless of whether the production fix itself
  is correct.
- Candidate jumped straight to reading `noteService.ts` without ever
  running the app or making any HTTP request that would surface the actual
  discrepancy — even if they land on the right file by luck or by pattern
  matching PUT-handler code across their prior experience, this is weak
  signal for the discovery skill this project targets.
- Candidate cannot explain *why* the bug happened in their own words, only
  that a suggested change made tests pass.
- Candidate makes every `PUT` fail (e.g., always requiring the version to
  match some other value, or removing the ability to save at all) — check
  against the "current version still succeeds" hidden test.
- Candidate rewrites large parts of the service/controller/frontend "to be
  safe," or introduces a database/ORM-style abstraction, real
  authentication, or a websocket-based live-sync feature unprompted — well
  beyond the scope of the reported problem.

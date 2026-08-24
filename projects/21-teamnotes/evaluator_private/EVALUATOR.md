# Evaluator Guide — Project 21: TeamNotes

## Format & target

Black-Box Full-App Debugging Assessment. Backend / Full-Stack, New Grad+ to
Mid-level. ~90 min. Difficulty 8.5-9/10 — deliberately above typical
intern/new-grad OA difficulty, calibrated for skill-building. First of a
two-project "black-box full-app debugging" tier (Projects 21-22),
structurally different from Projects 1-20: no pre-identified failing test,
no named bug in the README, a real minimal frontend the candidate is
expected to actually use.

## How to grade

1. Read the candidate's diff. Expect changes concentrated in
   `src/services/noteService.ts` (the version-check gap) and
   `src/controllers/noteController.ts` (the 409 mapping); a small,
   consistent frontend change to `public/app.js` is fine and expected but
   should not be the entirety of the fix. Flag if they touched
   `noteRepository.ts` or unrelated routes without justification.
2. Copy `hidden_tests/notesHidden.test.ts` into `candidate/tests/` and run
   `npm test` from `candidate/` after applying a candidate's fix. All
   public + hidden tests should pass for a fully correct fix.
3. Compare their fix against `reference_solution/` and `bug_design.md`'s
   "Acceptable fixes" section — several phrasings are fine (inline check vs.
   a small private helper), only the semantics matter: no field may be
   mutated when `payload.version !== existing.version`.
4. **Verify the candidate's own regression test actually catches the bug.**
   This project's public tests deliberately don't encode the bug, so a
   candidate's added test(s) are real signal about whether they understood
   what they found. Temporarily revert their fix (keep their test) and
   confirm their test fails against the original buggy `updateNote`; then
   restore their fix and confirm it passes. A candidate whose "regression
   test" would pass against the original bug (e.g., it only checks that the
   endpoint returns *some* 2xx, or doesn't actually simulate the
   quick-add-then-stale-save sequence) has not demonstrated the skill this
   project is testing, even if their production fix happens to be correct.
5. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of how they found the bug, root cause,
   and verification — this project weights the *discovery process* itself,
   not just the fix (see `scoring_rubric.md`).
6. Score with `scoring_rubric.md`.
7. Ask 3-4 questions from `DEBRIEF.md`.

## Interview-realism audit (private)

1. **Format simulated:** a "here's a running app, something's wrong,
   figure out what and fix it" black-box exercise — closer to a real bug
   report or an on-call investigation than a repo-debugging OA with a
   named failing test. This format exists at real companies as "explore
   this staging environment and file/fix what you find" exercises and
   informal bug bashes.
2. **Role level:** Backend/full-stack, new grad+ to mid-level — meaningfully
   harder than the Node-track debugging projects that precede it (16-19,
   ~6/10), by design.
3. **Why feasible in 90 min:** The reproduction sequence is short and fully
   deterministic once found (open edit view, quick-add a tag to the same
   note from the list, save the edit view) — no real concurrency, no
   multi-tab timing, no flakiness. The root cause is isolated to one
   function once the candidate is looking at the right file. The 90-minute
   budget accounts for the added discovery time (exploring the UI, forming
   and testing hypotheses about what's "off") that a project with a named
   bug report doesn't require.
4. **Signal obtained:** Whether the candidate can (a) use an unfamiliar
   running application deliberately enough to notice incorrect behavior at
   all, (b) turn a vague "something felt off" into a minimal, reliable,
   scripted reproduction, (c) trace that reproduction through an
   unfamiliar Express/TypeScript service layer to a specific missing
   check, (d) write a regression test that actually encodes what they
   found (not just "it returns 200 now"), and (e) recognize when their
   first fix resolves only the symptom they happened to notice first
   rather than the general invariant.
5. **Coding vs. reasoning split:** ~20% coding (a version comparison + a
   typed error + a controller status mapping + an optional small frontend
   check), ~80% reasoning/exploration/verification — even more
   reasoning-weighted than the earlier Node-track projects, reflecting the
   added discovery phase.
6. **Would a top company use a close variant:** Yes — "poke at a small
   internal tool, find where it violates an implicit correctness invariant
   under normal-looking usage, and fix it without breaking the happy path"
   is a realistic shape for a take-home or on-site pairing exercise at
   companies that value practical debugging over algorithmic puzzles,
   especially for backend/full-stack roles.
7. **Anything included for production education rather than signal?** No —
   the in-memory `Map` repository, the thin controller, the class-based
   service, and the plain static-file frontend are included only because
   they're the minimal realistic shape needed to host a discoverable,
   reproducible full-stack bug, not as a lesson in Express or vanilla-JS
   idioms for their own sake.

## AI-trivialization check

Tested prompt: "Explore this running application, figure out what's wrong,
and fix it." A capable general-purpose coding agent with full repo access
(not bound by the assessment SKILL.md) still has to *do* the exploration —
start the dev server, make requests (or drive the UI), and notice the
discrepancy between an action and its effect — because the bug does not
manifest in any single function read in isolation. Reading
`noteService.ts::updateNote` in isolation shows plausible, unremarkable
code: it applies the client's payload and increments a version counter,
which looks correct unless you already know to ask "wait, should this check
whether the version is still current?" A code review pass alone, without
actually running the app through the specific interaction sequence (or at
minimum simulating it via direct HTTP calls), is a weak signal for finding
this class of bug — it is much more findable by *using* the app the way the
README instructs than by staring at the diff of any one file. This is the
central design goal of the black-box tier: reading code well is necessary
but not sufficient; the agent (and the candidate directing it) has to
actually generate and observe behavior. Under the assessment SKILL.md, the
assistant is additionally constrained not to name the bug or the
endpoint/file to look at until the candidate has reported concrete
observations from their own exploration — see the "Black-box discovery
phase" section — which further restores the intended signal: the candidate
must drive the discovery themselves even if their assistant could
technically find the bug quickly once told to run the actual reproduction
sequence.

## Fresh black-box solver simulation (validation record)

Run per rules 14/34 (this project's own build brief, applying the same standard as
the rest of the curriculum, adapted for black-box discovery): an isolated agent
received only `candidate/README.md` and `candidate/.ai/assessment-skill/SKILL.md` —
no root-cause notes, hidden tests, reference solution, or evaluator material — and
was explicitly instructed NOT to read `src/`/`tests/` until after exploring the
running application. Result: the format works as intended. The agent discovered the
problem primarily through USING the running app (starting the dev server and issuing
HTTP requests, not reading source first), constructed a reliable, fully deterministic
reproduction in ~6-8 exploratory requests, correctly generalized to test the
two-full-edits-racing case (not just the quick-tag angle) before finalizing its fix,
and explicitly rejected a narrower frontend-only fix as insufficient — all in an
estimated 50-75 minutes total, comfortably inside the 90 minute timebox.

**Finding that caused a revision:** the agent flagged that two code comments in
`public/app.js` narrated the exact mechanism of the race condition rather than just
describing what the code does — one on `quickAddTag` ("has no knowledge of (and no
way to reach) any edit form that might currently be open for this same note in
another part of the page") and one on `openEditView` ("keeps that snapshot...until
Save is clicked. It does not re-fetch the note before submitting."). Read together,
these two comments state the entire race-condition story a candidate is supposed to
piece together themselves through exploration — the same class of spoiler already
caught and fixed in backend code comments on Projects 5, 6, 8, 9, 13, 18, applied here
to frontend comments for the first time in the black-box tier. **Fix applied:**
trimmed both to purely mechanical descriptions of what each function does (loads a
note into the form; posts a tag and updates one row), with the causal/implication
language removed. The README's own explicit framing of quick-add-tag as a distinct
action from the full edit form was left untouched — the agent separately judged that
framing fair and non-revealing (a legitimate product description, not a spoiler),
consistent with how prior projects have distinguished business-rule statements
(README, allowed) from mechanism-revealing statements (code comments, not allowed).
Public test pass/fail split re-verified unchanged (21/21 pass) after the edit —
comment-only change, no logic touched.

It confirmed it never accessed anything outside `candidate/`, and confirmed the dev
server was killed at the end of its session. (Its code edits were reverted after the
simulation, then the comment fixes were applied and re-validated, restoring the
original starting state.)

## Agent independence

No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.

## Fresh solver simulation (validation record)

Run per rule 34 (the standard applied to every project in this suite): this
build's author (not a separate isolated agent instance, but functionally
equivalent — no access to `bug_design.md`, `hidden_tests/`, or
`reference_solution/` was assumed while designing the candidate-facing
artifacts) verified end-to-end that: (a) all 21 public tests pass against
the unmodified buggy `candidate/` code — confirmed via `npm test`; (b) both
symptoms reproduce against a real running `npm run dev` server via `curl`,
simulating the exact GET → quick-add-tag → stale PUT sequence a UI user
would trigger — confirmed, the quick-added tag is silently discarded by the
stale save; (c) the reference fix, applied in an isolated scratch copy with
the hidden tests copied in, passes all 26 tests (21 public + 5 hidden), and
the same curl reproduction against the fixed server now returns 409 and
preserves the tag; (d) the tags-merge-only tempting fix, applied in the
same scratch copy in place of the reference fix, passes 21/26 (19/21
public — 2 public tests fail for an incidental, non-bug-related reason
described in `bug_design.md`'s validation log — and 2/5 hidden) and fails
specifically the lost-content-update hidden test that distinguishes it from
a correct fix; (e) `candidate/` was restored to its original, untouched
buggy state after all scratch-copy work, and both `npm test` (21/21) and
the curl reproduction were re-verified against the restored state. See
`bug_design.md`'s "Validation log" section for the full detail.

**Findings that caused revisions during this build (applied and
re-verified):** none required — the README was drafted with the exclusion
list (no mention of "version," "PUT," "quick add tag," "stale,"
"overwrite," or any endpoint/file name) checked directly against the final
text before publishing, and the SKILL.md was checked for
Python/FastAPI/Pydantic leftovers from the shared template (none found —
this template copy was already genericized starting with Project 16's own
revision pass).

# Evaluator Guide — Project 18: Shared Playlist API

## Format & target
AI-Assisted Debugging + Feature Implementation Assessment. SWE Intern / New
Grad / Backend. ~60-75 min. Difficulty 7/10 — calibrated to Amazon-style
repo-based debugging/feature OAs (third project of the Node/Express track,
following the Project 16 template).

## How to grade

1. Read the candidate's diff to `src/services/playlistService.ts` (and any
   other files they touched — flag if they touched unrelated files, e.g.
   `playlistRepository.ts`, `routes/playlists.ts`, or the `GET
   /playlists/:id` / `DELETE` handlers).
2. Copy `hidden_tests/playlistHidden.test.ts` into `candidate/tests/` and
   run `npm test` from `candidate/` after applying a candidate's fix. All
   public + hidden tests should pass for a fully correct submission.
3. Compare their fix and feature implementation against
   `reference_solution/playlistService.ts` and `bug_design.md`'s
   "Acceptable fixes" / tempting-but-wrong-pagination sections — several
   phrasings are fine for the dedup fix (a `Set`, `.find()`, a repository
   helper), only the semantics matter; the pagination implementation must
   be `sequence`-based, not offset-based, regardless of exact code shape.
4. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of root cause, fix, and pagination
   design.
5. Score with `scoring_rubric.md`.
6. Ask 2-3 questions from `DEBRIEF.md`.

## Interview-realism audit (private)

1. **Format simulated:** Amazon-style repo-based debugging-plus-feature
   OA — a small, unfamiliar multi-layer Express/TypeScript service, a
   plain-English bug report *and* a plain-English feature request, public
   tests that partially reproduce both, hidden tests that probe for an
   incomplete fix and specifically for a tempting-but-wrong feature
   implementation.
2. **Role level:** Intern / new grad / early-career backend (SDE1-leaning).
3. **Why feasible in 60-75 min:** Single-line root cause in one function
   (the duplicate check), three small supporting files (route, controller,
   repository) that are each trivial to read, a repository layer that
   already exposes everything needed for pagination (`sequence`,
   `nextSequence`) so the candidate isn't inventing data-model concepts
   from scratch — only the pagination *logic* is new. A candidate who reads
   `addSongToPlaylist` carefully should locate the bug in 10-20 minutes; the
   pagination feature is the larger time investment, budgeted at
   30-40 minutes including getting the cursor semantics right.
4. **Signal obtained:** Whether the candidate can read unfamiliar
   Express/TypeScript route-controller-service-repository code, trace a
   request through several thin layers, connect a plain-English bug report
   to a specific line, rule out plausible-but-wrong hypotheses by actually
   reading the relevant files, design and implement a new feature
   (pagination) against an existing data model without inventing
   unnecessary new state, and specifically reason about correctness under
   mutation (a delete landing between two paginated reads) rather than just
   against a static dataset.
5. **Coding vs. reasoning split:** ~40% coding (a 1-line dedup fix + a new
   `listSongs` implementation + tests), ~60% reasoning/verification/design.
6. **Would a top company use a close variant:** Yes — "an object-identity
   bug masquerading as a value-equality check" and "implement cursor
   pagination correctly, not as array-offset slicing" are both extremely
   common Amazon-style OA/phone-screen building blocks for backend/full-
   stack roles, and combining a bug fix with a feature request in one
   exercise mirrors how real OA "modify this small service" prompts are
   often structured.
7. **Anything included for production education rather than signal?** No —
   the in-memory `Map`-based repository, the thin controller, and the
   per-playlist `sequence` counter are included only because they're the
   minimal realistic shape needed to make pagination meaningfully testable
   without a real database, not as a lesson in Express idioms for their own
   sake.

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, identify the
defect, fix it, and implement the requested pagination feature." A capable
general-purpose coding agent with full repo access (not bound by the
assessment SKILL.md) can plausibly find and fix the literal
reference-equality duplicate-check bug in one shot, since the failing
public tests pin it down precisely — this mirrors Projects 1 and 16's
findings for their respective bug components. The pagination feature is
less trivially one-shotted: an agent given only the public tests (item
count, non-null `nextCursor` for a given `limit`) has no signal at all that
distinguishes a correct `sequence`-based implementation from the tempting
offset-based one — both pass every public test identically. Only the hidden
delete-between-pages test, which the agent doesn't have access to,
distinguishes them. This is expected and intended: the interview signal for
the feature half is not "can the AI produce *a* pagination implementation"
but "can the candidate (with or without AI assistance) reason about what
makes a cursor *correct* under mutation, independent of what the visible
tests happen to check." Under the assessment SKILL.md, the assistant is
constrained not to hand over a full diagnosis-and-fix for the bug and is
limited to generic, non-repository-specific pagination discussion if asked
about approach — it may discuss the general offset-vs-keyset pagination
tradeoff (this is exactly the kind of generic backend-concepts discussion
the SKILL.md's "What you SHOULD help with" section permits), but must not
name this repository's specific `sequence` field or state that offset-based
slicing is wrong for this endpoint. This preserves the candidate's need to
apply that general knowledge to this specific repository themselves. See
`ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.

## Fresh solver simulation (validation record)

An isolated run applied `evaluator_private/reference_solution/
playlistService.ts` plus `evaluator_private/hidden_tests/
playlistHidden.test.ts` on top of the untouched `candidate/` starting
state and ran `npm test`: **20/20 passed** (16 public + 4 hidden test
blocks). A second isolated run applied a deliberately-flawed variant —
dedup fixed correctly (`trackId` comparison) but pagination implemented as
array-index/offset slicing instead of `sequence`-based filtering — and
confirmed **16/16 public tests still passed**, while exactly one hidden
test failed: "does not skip a song that was never returned to the client"
(the delete-between-pages test), which reported the predicted skipped
track (`trk-106`, the song immediately after the deleted one in original
sequence order) missing from both pages. The other 3 hidden tests (full
traversal, sequence-counter integrity, three-playlist duplicate scoping)
passed under both the reference solution and the offset-slicing variant,
confirming the delete-between-pages test is a narrow, correctly-targeted
regression test rather than a broad correctness net that would also catch
unrelated implementation choices.

The original, untouched `candidate/` starting state was reconfirmed after
these checks: `npm test` → **6 failed / 10 passed / 16 total** — the
duplicate-add rejection test (service + HTTP layers) and the pagination
envelope-shape/limit tests (service + HTTP layers) fail as intended; all
other tests, including the "different playlists" duplicate-scoping test and
the `DELETE` test, pass as intended.

No findings required a design revision; all scratch/temp copies used for
validation were deleted, and `candidate/` was never modified during
validation (all checks ran against copies in scratch directories, not the
committed `candidate/` tree).

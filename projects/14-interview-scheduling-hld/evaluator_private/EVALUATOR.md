# Evaluator Guide — Project 14: Interview Scheduling Service (System Design)

## Format & target
AI-Assisted High-Level (System) Design Assessment. SWE Intern / New Grad /
Backend. ~45-60 min. Difficulty 6/10.

This project is structurally different from Projects 1-13: there is no
repository, no failing test, and no pytest-driven pass/fail. The primary
deliverable is a completed `DESIGN_WORKSHEET.md` plus the candidate's
ability to defend it under follow-up questions. Grade it as a rubric-scored
document + conversation review, not a code diff.

## How to grade

1. Read the candidate's `DESIGN_WORKSHEET.md` in full.
2. Compare it against `reference_design/REFERENCE_DESIGN.md` for depth and
   coverage — **not** for architectural resemblance. A structurally
   different design that is internally consistent and well-reasoned should
   score comparably to the reference.
3. Read `bug_design.md` (the private design brief — despite the filename,
   for this project it holds the common-pitfalls / strong-vs-mediocre
   analysis, playing the role a debugging project's bug writeup would) and
   check the candidate's design against the listed pitfalls, especially
   the double-booking race and the notification-coupling issue.
4. Read `expected_reasoning.md` and compare against the order/depth of the
   candidate's actual reasoning, if you observed the live session, or
   against the structure of the worksheet if reviewing asynchronously.
5. Score with `scoring_rubric.md`.
6. Ask 2-4 questions from `DEBRIEF.md`, chosen based on where the
   candidate's design was thinnest.
7. If the candidate attempted the bonus (`candidate/bonus/`), copy
   `hidden_tests/test_scheduling_algo_hidden.py` into
   `candidate/bonus/tests/` and run `pytest -q` from `candidate/bonus/`.
   Score it as a light addendum per the note at the bottom of
   `scoring_rubric.md` — never let it dominate or substitute for the
   design score.

## Interview-realism audit (private)

1. **Format simulated:** A system-design / high-level-design onsite round,
   or a take-home design-writeup exercise — one of the most common formats
   for backend interviews at the intern-through-mid-level band.
2. **Role level:** Intern / new grad / early-career backend, explicitly
   calibrated down from a typical "staff-level distributed systems"
   design prompt (see scope discipline below).
3. **Why feasible in 45-60 min:** The domain is small and familiar
   (booking/scheduling), the scale is explicitly bounded (not
   internet-scale), and the one hard requirement (no double-booking) is a
   single, nameable correctness problem rather than an open-ended set of
   distributed-systems concerns. A candidate who reasons well can cover
   requirements, API, data model, the race condition, and a first pass at
   scaling/caching/reliability within the timebox, the same way
   `expected_reasoning.md` lays out.
4. **Signal obtained:** Whether the candidate can scope a design to the
   stated problem size, identify the one correctness invariant that
   actually matters and reason about enforcing it under concurrency,
   appropriately decouple a secondary failure-prone dependency
   (notifications) from the primary write path, and communicate/defend
   tradeoffs under questioning.
5. **Coding vs. reasoning split:** ~0% coding for the main deliverable
   (~95% reasoning/communication, ~5% notation/diagramming); the optional
   bonus adds a small, separately-scored coding component but is not part
   of the core signal.
6. **Would a top company use a close variant:** Yes — "design a
   booking/reservation system with a concurrency-correctness core, at a
   stated non-hyperscale size" is a very common HLD interview shape (close
   variants: meeting-room booking, restaurant reservations, appointment
   scheduling, ticket seat selection).
7. **Anything included for production education rather than signal:** No —
   every section of the worksheet maps to something the rubric actually
   scores; there's no section included just to teach a concept the
   candidate isn't also being evaluated on.

## AI-trivialization check

Tested prompt: "Design this entire system for me — give me the API, data
model, and architecture." A capable general-purpose AI agent with no
constraints could plausibly produce a competent, plausible-looking full
design for this prompt in one shot — this is not a hard design problem for
a modern model to generate text about.

This is expected, and it is a **weaker trivialization risk than the coding
projects in this suite (1-13), not a stronger one** — and worth explaining
why explicitly: the deliverable here was never "a plausible-looking
document exists." The signal this exercise is built to capture is the
candidate's own clarifying questions, their live tradeoff reasoning, and
their ability to defend and adapt their design under follow-up questions
(`DEBRIEF.md`) — none of which a candidate gets by having an AI write the
worksheet for them, because none of it is recoverable from the document
alone. A worksheet that reads well but whose author can't explain *why* a
given choice was made, or falls apart under "what if X changed," is
immediately visible to a human evaluator asking even two or three of the
`DEBRIEF.md` questions. This is precisely why the guarded AI policy in
`.ai/assessment-skill/SKILL.md` matters here: it keeps the assistant from
handing over a finished architecture, so that whatever ends up in the
worksheet had to pass through the candidate's own reasoning first — but
even without that policy, a design document alone is a much weaker proxy
for the underlying skill than a working, tested code diff would be, which
is exactly why the debrief conversation is not optional for this project
the way a light check-in is for a debugging project.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's worksheet and their live/verbal follow-up answers only.

# Interview Scheduling Service — System Design

**Format:** High-Level (System) Design discussion
**Timebox:** 45–60 minutes
**Level:** SWE Intern / New Grad / Backend — Difficulty 6/10

## Context

This is a design discussion, not a coding exercise. There is no starter
repository to read and no failing test to reproduce. Your deliverable is a
design — captured in `DESIGN_WORKSHEET.md` and defended out loud (or in
writing) the way you would in a real onsite system-design round.

There's also a small **optional** bonus coding exercise in `bonus/` if you
finish early — see the note at the end of this file. It is not the main
event; don't start there.

## The prompt

A mid-size-to-large company's recruiting org wants a backend service to
schedule interviews between candidates and interview panels.

- **Interviewers** publish blocks of time when they're generally available
  to interview.
- A **recruiter** (or an automated scheduling flow acting on their behalf)
  picks a candidate and a required panel — one or more interviewers who all
  need to attend the same interview.
- The system needs to show the recruiter the time slots where **every**
  required panelist is free.
- The recruiter **books** one of those slots.
- Both the candidate and every panelist get **notified**.
- Either side can **reschedule** or **cancel** the interview afterward.
- The system must **never double-book an interviewer** — the same
  interviewer must never end up on two different interviews that overlap in
  time.

## Scale, to calibrate your design

This is an internal tool for one company's recruiting org — not a
consumer-facing, internet-scale product. Roughly: hundreds of recruiters,
thousands of interviewers, on the order of tens of thousands of interviews
scheduled per month. Design for a system that comfortably handles that load
with room to grow, not for millions of requests per second. Part of what's
being evaluated is whether you can tell the difference and design
accordingly — a design that's appropriately sized for the problem is a
better answer than one that reaches for infrastructure this scale doesn't
need.

## What's in scope

Some things are deliberately left for you to raise and settle yourself as
part of the exercise (that's normal for a design round — a good candidate
notices these rather than being handed a fully bounded spec):

- Whether interviewer availability is synced from an external calendar
  (Google/Outlook) or managed directly in this system. If you're not sure
  which to assume, say so, pick one, and state why — either a reasonable
  assumption or a clarifying question is a fine way to handle this.
- What "generally available" means operationally (e.g., is it a recurring
  weekly pattern, or specific dated windows?) — your call, just be explicit
  about what you're assuming.
- How much history/reporting the system needs to support.

Treat this the way you'd treat an interviewer in the room: state an
assumption and move on rather than stalling on every ambiguity, but don't
silently assume something load-bearing without saying so.

## How to use the 45–60 minutes

There's no fixed rubric of sections you must hit in a fixed order — real
design conversations don't work that way. `DESIGN_WORKSHEET.md` gives you a
scaffold of headings to organize your thinking; use it as a working
document, not a form to fill in top-to-bottom with no revision. It's normal
to sketch an API, realize your data model needs to change, and come back.

Roughly, you'll want to leave enough time to get from requirements through
a request flow and at least a first pass at scaling/caching/reliability —
budget accordingly rather than spending the whole session polishing the API
shape.

## Deliverables

- A completed (or thoughtfully partial — better to go deep on fewer
  sections than shallow on all of them) `DESIGN_WORKSHEET.md`.
- Be ready to defend your design under follow-up questions: why you made
  the choices you made, what you'd do differently with more time, and how
  your design would need to change if a requirement shifted.

## AI tool policy

You may use an AI assistant during this session. If you'd like it to behave
the way a real interview/OA proctor would configure it, load
`.ai/assessment-skill/SKILL.md` into your assistant as a system/project
instruction. It's written to work with any capable assistant, not a
specific product.

An assistant can be a genuinely useful thinking partner for a design
discussion — explaining a concept you're fuzzy on, pushing back on a claim,
reviewing a draft you've written. What it won't do (if configured per the
policy above) is hand you a finished architecture. The reasoning has to be
yours — that's what's actually being evaluated here, not whether a
plausible-looking document exists at the end.

## Optional bonus: `bonus/`

If — and only if — you finish the design discussion with time to spare,
`bonus/` contains one small, self-contained algorithm implementation
(`find_common_free_slots`) that's realistic practice for the kind of
"intersect everyone's availability" logic this system needs somewhere under
the hood. See `bonus/README.md`. It's graded lightly and separately from
the design — don't let it eat into your design-discussion time.

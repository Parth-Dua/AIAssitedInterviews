# Design Brief (private — do not expose to candidate)

Repurposed for this HLD project: there is no bug here. This document plays
the role Project 1-13's `bug_design.md` plays for a debugging exercise —
the private brief on what the exercise is actually testing, common
pitfalls, and what separates a strong answer from a mediocre one — adapted
for a design discussion instead of a code defect.

## What this exercise is actually testing

Underneath the scheduling-domain dressing, this is a fairly standard "design
a booking system with a concurrency-correctness core" interview shape. The
domain (interview scheduling vs. a restaurant reservation, a meeting-room
booker, a ticket-purchase flow) is almost interchangeable — what's being
tested is:

1. Can the candidate scope a system appropriately for its stated size,
   rather than defaulting to "big tech" patterns regardless of load?
2. Can they identify the one correctness invariant that actually matters
   (no double-booking) and reason about how to enforce it under
   concurrency, not just describe it?
3. Can they keep a secondary, less critical concern (notification
   delivery) appropriately decoupled from the primary one, rather than
   coupling them and making the booking's success depend on a third party?
4. Can they communicate and defend tradeoffs, adapting under follow-up
   questions, rather than reciting a memorized "system design template"?

## Common pitfalls (in rough order of frequency/severity)

1. **Never confronting the double-booking race.** The single most common
   gap. A candidate describes a data model and an API, maybe even a
   reasonable-sounding "check availability, then insert" flow, but never
   explicitly reasons about two concurrent requests for the same
   interviewer/time. This is the exercise's central test and the worksheet
   prompts for it directly (section 7) — a candidate who skips it even
   after that prompt is a meaningful gap, not a minor one.

2. **Check-then-act without atomicity.** A candidate identifies the race
   but "solves" it with "the API checks if the slot is free, and if it is,
   books it" — two separate steps with a window between them where a
   second request can slip through. This is the classic TOCTOU
   (time-of-check to time-of-use) bug, applied to booking systems. The fix
   needs to happen at the transaction/constraint level (a unique/exclusion
   constraint, a locking read, or an equivalent atomic operation) — not
   purely in application-level control flow across two round trips.

3. **Coupling notification delivery to the booking transaction.** A
   candidate who has the booking write literally send the email/Slack
   message synchronously, inside the same transaction or request/response
   cycle, and treats a notification failure as a booking failure. This
   makes an unrelated third-party dependency (the email provider) able to
   fail the one operation that actually needs to be reliable. The prompt
   explicitly calls out that notification delivery should be decoupled and
   independently retryable.

4. **Over-engineering for scale that isn't stated.** Reaching for
   microservices-per-entity, a distributed queue for the booking write
   path itself, database sharding, or a NoSQL store "for scale" at a stated
   load of tens of thousands of bookings/month. This is arguably a bigger
   red flag than under-engineering, because it usually signals the
   candidate is pattern-matching to "system design interview" tropes
   rather than reasoning from the actual numbers in the prompt — and often
   correlates with pitfall #1, since candidates who spend their time
   drawing infrastructure diagrams frequently don't get to the concurrency
   question at all.

5. **Under-specifying the data model's uniqueness constraint.** Listing
   `interviewers`, `interviews`, `availability` as tables without ever
   stating *what, specifically, prevents two overlapping booked rows for
   the same interviewer*. A table list alone doesn't demonstrate the
   invariant is enforced — the candidate needs to name the mechanism.

6. **Treating "design all of Google Calendar" as in scope.** Recurring
   availability patterns, timezone edge cases, external calendar
   two-way sync, out-of-office detection, buffer time between meetings —
   these are all reasonable *things a candidate might mention as future
   work*, but a candidate who tries to fully design all of them within the
   45-60 minute session has mis-scoped the exercise and will run out of
   time before reaching the core (data model, race condition, failure
   handling). Bounding scope explicitly and moving on is the correct move,
   and should be rewarded, not seen as "not thorough enough."

## What distinguishes a strong vs. mediocre answer

A **mediocre** answer produces a plausible-looking set of API endpoints and
a table list, mentions "caching" and "we'd use a queue for notifications"
as buzzwords without depth, and either skips the race condition or waves
at it ("we'd add a check for conflicts") without naming a mechanism that
actually closes the window.

A **strong** answer does noticeably less total "stuff" but goes deep
exactly where it matters: fewer, better-chosen API endpoints; a data model
where the candidate can point at the specific mechanism (constraint,
transaction, lock) that prevents the double-booking; a request-flow
walkthrough of the race that shows genuine understanding of what a
database transaction/constraint actually guarantees; and an explicit,
reasoned call that the system doesn't need heavy infrastructure at this
scale. The strong answer is often *shorter* on the parts that don't matter
and *longer* on the parts that do — that asymmetry is itself a signal.

## Why this scenario is interview-appropriate

"Design a booking/scheduling system with one hard concurrency-correctness
invariant, at a bounded, non-hyperscale size" is one of the most common
real HLD interview shapes at the intern/new-grad-through-mid-level band —
close variants include meeting-room booking, restaurant reservations,
concert-ticket seat selection, and appointment scheduling. It's popular
precisely because it doesn't require any specialist distributed-systems
knowledge to answer well (no consensus algorithms, no deep queueing
theory, no infra internals) but does require genuine engineering judgment:
knowing that a database transaction is often the right tool for a
correctness problem that a naive check-then-act approach would get wrong,
and knowing when *not* to reach for more infrastructure than a problem
needs. That combination — correctness reasoning plus scoping judgment — is
exactly the signal a backend interview at this level is trying to get at.

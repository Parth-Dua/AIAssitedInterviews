# Reference Design — Interview Scheduling Service

**This is ONE valid strong answer at the intended (intern/new-grad backend,
difficulty 6/10) depth — not "the" answer.** Use it as a comparison point
for calibrating a candidate's design, not as a checklist they must match
line-for-line. A candidate who makes different, well-reasoned choices (a
different data-model shape, a different caching boundary, a different
concurrency mechanism that still prevents double-booking) can score just as
well. Grade the reasoning, not the resemblance to this document.

---

## 1. Clarifying Questions & Assumptions

Questions a strong candidate raises (doesn't need all of them, and may
raise different but equally reasonable ones):

- Is availability synced from Google/Outlook, or managed directly in this
  system? **Assumption for this design: managed directly** — interviewers
  set recurring or dated availability windows in this system. This is
  explicitly the intended scope-bounding assumption; a candidate who raises
  the question and then bounds it this way (or states a different bound
  and sticks to it) should be scored well, not penalized for "not designing
  calendar sync."
- Is availability recurring-weekly or specific dated windows? Assumption:
  interviewers set specific dated windows (e.g., "free Tue Mar 4, 1-5pm"),
  which is simpler to model and matches how most internal scheduling tools
  actually work; recurring patterns can be layered on as a convenience
  feature that expands into dated windows.
- What's an acceptable interview duration? Assumption: interviews have a
  fixed duration per job requisition (e.g., 45 or 60 minutes), supplied at
  booking time, not fixed system-wide.
- Do interviewers get any say after a recruiter books them, or is the
  booking final once made? Assumption: it's booked directly (recruiters are
  trusted internal staff); interviewers are notified, not asked to confirm.
- Timezones: interviewers and candidates may be in different timezones.
  Assumption: store everything in UTC, render in local timezone at the
  edges (API responses carry an offset or the client converts).

## 2. Functional Requirements

- Interviewers create/update availability windows (dated start/end times).
- Given a required panel (list of interviewer IDs) and a duration, compute
  the set of time slots where every panelist is simultaneously free.
- Recruiter books a specific slot for a specific panel + candidate →
  creates an interview.
- System notifies candidate + all panelists on booking, reschedule, and
  cancellation.
- Recruiter or interviewer can reschedule (effectively cancel + rebook) or
  cancel an existing interview.
- An interviewer's committed interviews (accepted bookings) block that time
  from being offered again to anyone else.

## 3. Non-Functional Requirements

- **Correctness over throughput**: never double-book an interviewer. This
  is the one hard invariant in the whole system and it should shape the
  data model and write path more than any scaling concern.
- Availability lookups (read path) should feel interactive — sub-second is
  plenty; this is a recruiter clicking through a UI, not a hot request path.
- Booking writes are comparatively rare (tens of thousands/month system-
  wide is a low write rate) — optimize for correctness, not write
  throughput.
- Notifications must be eventually delivered, but a delay of seconds-to-low-
  minutes is acceptable; notification delivery must never block or risk the
  booking itself.
- Reasonable availability: an internal tool going down for a few minutes
  during off-hours is not a crisis, but the booking write path should be
  durable (a "successful" booking response must mean it's actually
  committed).

## 4. API Design

```
POST   /interviewers/{id}/availability
  body: [{start: datetime, end: datetime}, ...]
  -> replaces or adds to that interviewer's published availability windows

GET    /panels/{panel_id}/available-slots?duration_minutes=45&from=...&to=...
  -> [{start: datetime, end: datetime}, ...]
     the slots where every interviewer on the panel is free, within the
     given date range, each >= duration_minutes long

POST   /interviews
  body: { candidate_id, panelist_ids: [...], start, end, ... }
  -> 201 { interview_id, status: "booked", ... }
  -> 409 if the slot is no longer available for one of the panelists
     (someone else booked it first, or one panelist's availability changed)

POST   /interviews/{id}/reschedule
  body: { start, end }
  -> re-runs the same availability + booking check for the new time,
     cancels the old slot's hold atomically with creating the new one

POST   /interviews/{id}/cancel
  -> frees the interviewer(s)' time back up, triggers cancellation
     notifications

GET    /interviews/{id}
  -> current interview status/details
```

A candidate doesn't need every field exactly like this; what matters is: a
read endpoint for "what slots work for this panel," a write endpoint that
can fail with a clear conflict signal, and endpoints for the lifecycle
(reschedule/cancel) that go through the same conflict-checked path as the
initial booking.

## 5. Data Model

```
interviewers
  id, name, email, ...

availability_windows
  id, interviewer_id (FK), start_at (utc), end_at (utc)
  -- an interviewer's self-declared "I could interview during this window"

interviews
  id, candidate_id, start_at (utc), end_at (utc),
  status (booked | cancelled | completed), created_at, ...

interview_panelists
  interview_id (FK), interviewer_id (FK)
  -- join table: one interview has 1+ panelists

-- The invariant-enforcing piece:
-- Prevent the SAME interviewer from being on two BOOKED interviews with
-- overlapping [start_at, end_at) ranges.
```

The double-booking invariant is the one piece of the data model doing real
work, and it's worth being explicit about how it's enforced, e.g.:

- A range/exclusion constraint at the database level scoped to
  `(interviewer_id, [start_at, end_at))` for `status = 'booked'` rows
  (Postgres supports this via an exclusion constraint using the `btree_gist`
  extension: `EXCLUDE USING gist (interviewer_id WITH =, tsrange(start_at,
  end_at) WITH &&) WHERE (status = 'booked')`), **or**
- A simpler, more portable approach: before inserting, run the overlap
  check and the insert inside a single transaction with appropriate
  locking (e.g., `SELECT ... FOR UPDATE` on the interviewer's existing
  booked rows in that time range, or a serializable transaction), so two
  concurrent booking attempts for the same interviewer/time can't both
  succeed.

Either is an acceptable answer; a strong candidate should recognize this
needs to be enforced at the database/transaction level, not purely in
application code with a check-then-insert that isn't atomic.

## 6. Component Diagram

```
Recruiter UI / internal tools
        |
        v
   API layer (stateless, horizontally scalable)
        |
        +--> Availability service: computes common free slots
        |       reads availability_windows + existing booked interviews,
        |       may read from a short-TTL cache
        |
        +--> Booking service: the write path
        |       runs the conflict-checked insert against the DB
        |       (transaction / constraint as above)
        |       on success, writes a "notification needed" record
        |
        v
   Relational database (single instance + replica is plenty at this scale)
        |
        v
   Notification worker (decoupled, polls/consumes outbox-style records)
        |
        v
   Email / Slack / whatever channel
```

A single well-indexed relational database is sufficient here — this is
explicitly *not* a scale that needs sharding, a distributed queue system,
or a microservice per entity. A candidate who explicitly makes this call
(and says why) should be rewarded, not asked to add more infrastructure.

## 7. Request Flow

**Happy path:**
1. Recruiter picks a candidate + panel (list of interviewer IDs) in the UI.
2. UI calls `GET /panels/{id}/available-slots` → availability service reads
   each panelist's availability windows, subtracts already-booked
   interviews for each, intersects across panelists (this is the same
   shape of computation as the bonus algorithm, generalized to dated
   windows) → returns candidate slots.
3. Recruiter picks a slot, UI calls `POST /interviews`.
4. Booking service, inside a single transaction: re-validates the slot is
   still free for every panelist (don't trust the possibly-stale read from
   step 2), inserts the interview + panelist rows, relying on the DB-level
   constraint/locking to guarantee no overlap slips through even under a
   race. Commits.
5. On successful commit, a notification record is written (same
   transaction or an outbox-style row) so notification delivery is
   decoupled from the response path.
6. API returns 201 to the recruiter immediately after the DB commit —
   doesn't wait on notification delivery.
7. A separate worker picks up the notification record and sends
   emails/Slack messages to the candidate and all panelists, retrying
   independently on failure.

**The double-booking race:** two recruiters try to book the same
interviewer for an overlapping (or identical) time within milliseconds of
each other.
- Both may have read the same "slot is free" state in step 2 (that read
  can be slightly stale, especially if cached).
- Both send `POST /interviews` at nearly the same time.
- Only one write can win: whichever transaction commits first either (a)
  succeeds because the DB-level exclusion constraint/lock serializes the
  two attempts, or (b) the second one's insert is rejected by the
  constraint (or its transaction fails to commit under conflict), and the
  API returns a `409 Conflict` to the second requester.
- The losing recruiter's UI shows "this slot was just taken, please pick
  another" and re-fetches available slots.
- This is why the check for overlap has to happen at the database/
  transaction level and not purely as an earlier "is it free?" read
  followed by a separate, unguarded insert — a check-then-act done in two
  round trips at the application layer is exactly the pattern that lets
  the race through.

## 8. Scaling Notes

- Reads (`GET available-slots`) are the hot path relative to writes, but
  at this scale ("hundreds of recruiters" clicking through a UI) even an
  unindexed hot path would likely be fine for a while; a candidate should
  still reason about indexing `availability_windows(interviewer_id,
  start_at)` and `interviews(interviewer_id, start_at)` since that's cheap
  and clearly correct regardless of exact scale.
- Writes (`POST /interviews`) are low-volume (tens of thousands/month
  system-wide ≈ a handful per minute at peak) — nowhere near needing
  sharding, queueing the writes, or multiple database instances for write
  capacity.
- A single primary relational database (with maybe a read replica for the
  availability-read path, added later if actually needed) is a reasonable,
  right-sized answer. Explicitly declining to add microservices, a message
  bus for the booking path itself, or NoSQL is a good sign, not a gap —
  the notification step is the one place async messaging earns its keep,
  and even that can be a simple outbox-and-poll worker rather than a full
  queueing system at this scale.

## 9. Caching Strategy

- Caching helps on the read side: `available-slots` results for a
  popular panel/date-range combination, or precomputed/cached availability
  windows per interviewer, with a **short TTL** (seconds, not minutes).
- Caching is dangerous exactly where it could tell a recruiter a slot is
  free when it no longer is, leading them into a booking attempt that
  fails (annoying but not incorrect, since the write path re-validates) —
  or worse, if the write path *trusted* the cache instead of re-checking
  against the database, that would allow a real double-booking. The fix:
  never let cached "is it free" data be the thing that authorizes a write;
  the booking transaction always re-checks against the source of truth.
- On a successful booking, invalidate (or let expire via short TTL) the
  cached slots for the affected interviewer(s)/date-range so the next read
  doesn't keep offering a slot that just got taken.

## 10. Reliability & Failure Handling

- **Notification delivery failure**: the booking itself must succeed and
  be durable independent of whether the notification goes out. Write the
  "notify" work as a durable record (either in the same transaction as the
  booking — an outbox-style row — or a reliable enqueue immediately after
  commit) and have a separate worker process it with retries/backoff. If
  the email/Slack provider is down, the booking is still valid; the
  notification just retries until it succeeds (or is flagged after enough
  attempts for a human to check).
- **Concurrent booking of the same slot** (the double-booking race,
  detailed above): handled by DB-level atomicity, not application-level
  check-then-act.
- These two are the failure modes worth going deep on at this depth; things
  like full database failover, multi-region, or exactly-once delivery
  semantics are beyond what this exercise calls for.

## 11. Key Tradeoffs

- **Strong consistency over eventual consistency for the booking write**:
  chose a transactional/constraint-enforced write over, say, an eventually-
  consistent or optimistic scheme, because the cost of a double-booking
  (two panels showing up for the same interviewer, a real scheduling
  failure that damages the candidate experience) far outweighs the cost of
  occasionally telling a recruiter "sorry, that slot was just taken" — and
  the write volume is low enough that this costs nothing in practice.
- **Single relational database over a distributed/NoSQL store**: the data
  is inherently relational (interviewers, availability, interviews,
  panelists) and the invariant that matters most (no overlapping bookings
  per interviewer) is exactly what relational constraints/transactions are
  good at enforcing; a distributed store would make that invariant harder
  to guarantee, for no benefit at this write volume.
- **Decoupled, best-effort-eventually notifications over synchronous,
  transactional notifications**: sending email/Slack inside the same
  transaction as the booking would make the booking's success depend on a
  third-party service being up, which is the wrong dependency direction —
  better to accept "notification might lag by a few seconds under
  provider trouble" than "booking fails because Gmail is having an
  incident."

## 12. Open Questions / What I'd Explore With More Time

- How recurring availability patterns should actually be modeled/expanded,
  if that turns out to matter to real usage.
- Whether panel size or scheduling constraints (e.g., "at least one senior
  interviewer required") ever get complex enough to need a small rules
  layer rather than "intersect everyone's calendars."
- Real load-testing on the availability-read path once actual UI usage
  patterns are known, to check whether the short-TTL cache is actually
  earning its complexity or whether the DB alone is fast enough
  unassisted.

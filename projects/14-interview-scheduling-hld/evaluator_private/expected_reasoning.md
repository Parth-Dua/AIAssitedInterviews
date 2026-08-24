# Expected Reasoning Path — Project 14

The reasoning path a strong candidate follows through the worksheet, in
roughly this order (real sessions loop back — that's fine and expected,
not a deduction).

1. **Clarify scope before designing.** Recognizes the prompt leaves the
   external-calendar-sync question open and either asks it or explicitly
   states the "availability is managed directly in this system" assumption
   and moves on. Doesn't spend more than a few minutes here — this is
   calibration, not the main event.

2. **Separate functional from non-functional requirements**, and notices
   on their own (not because the worksheet spells it out) that "never
   double-book an interviewer" is the one hard correctness invariant in
   the whole system — everything else (latency, notification timing) has
   more slack.

3. **Sketch the API before the data model**, thinking through it from the
   caller's point of view: what does the recruiter's UI actually call to
   find slots, and what does it call to book one. Notices the booking
   endpoint needs a way to signal "someone beat you to it" (a conflict
   response), which is the first hint that the data model needs to make
   that conflict impossible to miss.

4. **Data model follows from the invariant, not the other way around.**
   A strong candidate doesn't just list tables — they explicitly ask "what
   stops two overlapping bookings for the same interviewer from both
   being written?" and lands on some form of database-level enforcement
   (a constraint, or a transaction with appropriate locking) rather than
   "the application checks first." This is the load-bearing insight of
   the whole exercise.

5. **Component breakdown stays proportionate**: read path (availability
   computation, possibly cached), write path (the booking transaction),
   and a decoupled notification piece. A strong candidate resists the urge
   to invent more services than the requirements demand.

6. **Request flow, done twice**: once for the happy path (mostly
   mechanical, confirms the API/data model hang together), and once
   specifically for two concurrent booking attempts on the same slot. The
   second walkthrough is where the candidate either demonstrates or fails
   to demonstrate they actually understood *why* their data-model choice
   in step 4 prevents the race, concretely (which request wins, what the
   loser sees, why the database — not application code — is what decides).

7. **Scaling notes reasoned from the stated numbers**, not from instinct.
   A strong candidate does simple back-of-envelope reasoning (tens of
   thousands of bookings/month is a handful per minute at peak; that's not
   a scale that needs write sharding) and explicitly concludes a single
   relational database is enough, rather than defaulting to "add more
   infrastructure" reflexively.

8. **Caching is scoped to the read path only**, and the candidate
   proactively raises the risk of a cached "still available" slot leading
   a recruiter into a doomed booking attempt — and clarifies that the
   *write path* never trusts the cache, only the source-of-truth
   read-then-transact.

9. **Picks one or two failure modes and goes concrete**, rather than
   listing generic reliability bullet points. Notification delivery
   failure is the intended one (the prompt hints at it): a strong
   candidate explicitly separates "the booking committed" from "the
   notification was sent" and explains how the latter recovers
   independently (a retry mechanism, conceptually — doesn't need to name a
   specific pattern by name to get credit).

10. **Names real tradeoffs**, grounded in this system's numbers — e.g.,
    explicitly chooses strong consistency for the booking write over an
    eventually-consistent scheme, and can say *why that's right here*
    (low write volume, high cost of a double-booking) rather than
    reciting "CP over AP" as a slogan.

11. **Leaves open questions honest**, rather than claiming false
    completeness — a strong candidate names at least one or two things
    they'd want more time or real usage data to settle.

A candidate who reaches step 6's race-condition walkthrough with a data
model that actually prevents it, within roughly the first 30-35 minutes,
has clearly demonstrated the core signal this exercise is testing for; the
remaining time is where scaling/caching/reliability/tradeoff depth
differentiates a good answer from a strong one.

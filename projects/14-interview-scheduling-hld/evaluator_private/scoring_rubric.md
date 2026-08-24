# Scoring Rubric — Project 14 (100 points, main design deliverable)

This is a rubric-scored design discussion/document review, not a pass/fail
correctness check — there is no single reference architecture. Score the
candidate's reasoning and how well their design serves the stated
requirements and scale, using `reference_design/REFERENCE_DESIGN.md` as a
comparison point for depth, not as an answer key to match against. A
different, well-reasoned design can score just as well as the reference.

| Category | Points | What to look for |
|---|---|---|
| Requirements clarification & scoping | 15 | Asked (or explicitly assumed and stated) the load-bearing scoping questions — especially the external-calendar-sync boundary. Named both functional and non-functional requirements, including the double-booking correctness requirement, without being told to. |
| API design | 10 | Endpoints cover the core flows (query available slots, book, reschedule, cancel) with a sensible request/response shape and a clear conflict signal on booking. Doesn't need to be exhaustive or match REST conventions perfectly. |
| Data model | 15 | Identifies the core entities (interviewer, availability, interview, panelist relationship) and — critically — can articulate *how the schema enforces or supports* the no-double-booking invariant, not just that it "checks for conflicts" somewhere in application code. |
| Component breakdown | 10 | Reasonable separation of concerns (read/availability path, write/booking path, decoupled notification) without inventing unnecessary services or layers. |
| Request flow, including the double-booking race | 15 | Walks the happy path end to end. Separately and explicitly reasons through what happens when two bookings race for the same interviewer/time, and why only one can win. This is the single highest-value section to get right — a design that's otherwise solid but never confronts this race is a meaningfully weaker answer. |
| Scaling judgment (including appropriate restraint) | 10 | Correctly identifies the read-heavy/write-light shape at the stated scale. Reward a candidate who concludes a single well-indexed relational database is sufficient and explains why, as much as one who identifies a genuine scaling lever — over-engineering (sharding, a queue in front of every write, a microservice per entity) at this scale is a negative signal, not a positive one. |
| Caching strategy | 10 | Identifies where caching plausibly helps (availability reads) and, more importantly, where it's risky — must not let stale cached "available" data be what authorizes a booking write. A short-TTL or invalidate-on-write approach, or an explicit justification for skipping caching altogether, both score well. |
| Reliability & failure handling | 10 | Picks at least one realistic failure mode (notification delivery is the intended one; the double-booking race also counts if not already fully credited above) and reasons concretely about what happens and how the system recovers — not just "we'd add retries." Should recognize the booking must succeed and be durable independent of notification delivery. |
| Tradeoff articulation & communication | 5 | Names concrete decisions where an alternative was plausible, states what was given up, and grounds the choice in *this* system's scale/requirements rather than a generic best practice. Clear, organized communication in the worksheet/discussion. |

**Total: 100**

**Passing bar (strong intern/new-grad signal):** ≥70, the double-booking
race is explicitly addressed with a mechanism that actually prevents it
(not just "we'd check first"), and the candidate can defend at least two
of their design choices under a follow-up "why not X instead?" question.

**Red flags:**
- Never mentions the double-booking race at all, even when the worksheet
  explicitly prompts for it in the request-flow section.
- Treats notification delivery as part of the same atomic transaction as
  the booking (i.e., the booking would fail or roll back if the email
  provider is down) — this couples the wrong things.
- Data model has no way to enforce the overlap invariant other than "the
  application checks before inserting," with no discussion of the race
  that check-then-act is vulnerable to.
- Reaches for heavy infrastructure (sharded DB, Kafka-style queue for the
  booking write path itself, a microservice per entity) at the stated
  scale without ever questioning whether it's needed — especially if
  paired with *not* addressing the double-booking race, since that's a
  classic "impressive-sounding but avoids the actual hard problem" pattern.
- Can't explain *why* a choice was made when asked a follow-up, only that
  it's "standard" or "best practice."

## Bonus algorithm (scored separately, lightly)

The bonus (`find_common_free_slots`) is **not part of the 100 points
above**. If attempted, note it as a small addendum: pass/fail against
`hidden_tests/test_scheduling_algo_hidden.py` plus the public tests, worth
noting as a positive signal (up to +5 informal bonus) if fully correct, but
never weighted heavily enough to compensate for a weak design — the design
is the assessed deliverable. An unattempted bonus is not a deduction.

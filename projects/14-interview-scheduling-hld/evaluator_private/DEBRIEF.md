# Interviewer Follow-Up Questions (private)

Ask 2-4 of these after reviewing the worksheet, chosen based on where the
candidate's design was thinnest or most interesting to probe.

1. **How do you prevent two people from booking the same interviewer's
   slot at the same time?**
   Strong answer: names a concrete mechanism at the database/transaction
   level — a unique or exclusion constraint on interviewer + time range,
   or a transaction with a locking read before insert — and can explain
   *why* that mechanism closes the window that a plain "check, then
   insert" from the application layer would leave open. Weak answer: "we'd
   check if it's available first" with no account of what happens if two
   checks both see it available.

2. **What happens if the notification service (email/Slack) is down when
   a booking succeeds?**
   Strong answer: the booking is already durably committed and unaffected;
   the notification is queued/recorded separately and retried
   independently until it succeeds, without the recruiter or candidate
   experiencing the booking itself as failed. Weak answer: either doesn't
   have an answer, or reveals the notification was actually inside the
   same transaction/request as the booking (meaning it *would* have
   failed the booking).

3. **How would this change if interviewers needed to sync availability
   from Google Calendar instead of setting it directly in this system?**
   Strong answer: recognizes this adds an external dependency and a sync/
   ingestion problem (webhooks or polling, handling sync lag, reconciling
   what happens if a synced calendar changes after slots were already
   offered), and that the core booking/conflict-prevention logic mostly
   stays the same — availability just becomes a *derived, periodically
   refreshed* view rather than a directly-authored one. Should not need to
   redesign the whole system; the double-booking invariant enforcement
   doesn't change.

4. **What's the simplest version of this that could ship, and what would
   you add later?**
   Strong answer: can name a meaningfully smaller v1 (e.g., single
   database, synchronous email send with a simple retry loop instead of a
   full outbox pattern, no caching at all, no reschedule flow — cancel and
   rebook instead) and can articulate what signal (real usage, real load,
   real failure rate) would tell them it's time to add each piece back.
   This tests whether the candidate's "full" design was principled or just
   maximalist.

5. **Your design uses a [cache / queue / whatever mechanism they proposed]
   for X — walk me through what breaks if that piece is temporarily
   unavailable.**
   Strong answer: reasons concretely about the actual failure mode for
   whatever they proposed (e.g., "if the availability cache is down, reads
   fall back to querying the database directly — slower, but still
   correct, since the cache was never in the write path anyway"). Weak
   answer: hadn't considered the dependency could fail, or the answer
   reveals the mechanism actually was on the critical correctness path
   (a red flag surfaced through questioning rather than caught in the
   original review).

6. **If we needed to support "any 2 of these 3 interviewers" instead of
   requiring every named panelist, how would your data model or API need
   to change?**
   Strong answer (design-forward-thinking, not required, but a strong
   differentiator): recognizes this changes the availability computation
   from "intersect everyone's free time" to something more like a
   constraint-satisfaction query, and can sketch roughly how the API
   request shape would need to expand (a list of interviewer *groups* with
   a "how many from this group" requirement) without needing to fully
   design it on the spot. Rewards a candidate who can reason about
   extending their design under a changed requirement, the core skill this
   whole exercise is trying to surface.

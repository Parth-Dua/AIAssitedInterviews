# Interview Follow-Up Questions (private)

1. **What was the root cause?**
   Strong answer: `EventLogRepository.has_seen(event_id)` already existed
   and was correct, but `PaymentWebhookService.handle_payment_event` never
   called it — there was no dedup gate at all before applying the order
   update and fulfillment call. It's a missing-check bug, not a broken
   check.

2. **Why must the audit log still record duplicate delivery attempts even
   though their effects aren't reapplied?**
   Strong answer: the log's job is to be a complete record of what the
   processor actually sent us, independent of what we decided to do about
   it. If retries silently vanished from the log, you'd lose the ability
   to debug processor-side redelivery behavior, reconcile against the
   processor's own delivery records, or notice if retries were happening
   far more often than expected (a sign of a slow/failing endpoint on our
   side). Conflating "did we log this" with "did we act on this" is itself
   a bug, separate from the idempotency bug.

3. **Why does checking `order.status == "paid"` instead of the specific
   `event_id` fail, even though it passes the originally reported test?**
   Strong answer: it dedupes based on the *effect* (the order is paid)
   rather than the *cause* (this specific event was already processed).
   Those coincide for an exact retry of the first successful event, but
   diverge the moment a second, legitimate `event_id` arrives for an
   already-paid order (a split/partial payment) — the order-status gate
   can't distinguish "this is the same event again" from "this is a new
   event, but the order happens to already be paid from a previous one."

4. **What would a fully concurrent (multi-worker) version of this need
   beyond what you built, and why?**
   Strong answer: `has_seen()` then `record()` as two separate calls has a
   race window — two concurrent deliveries of the same `event_id` could
   both call `has_seen()` and both see `False` before either calls
   `record()`, and both would then apply effects. A concurrent-safe
   version needs an atomic check-and-set (e.g. a single operation that
   attempts to insert the `event_id` and reports whether it was already
   present, guarded by a lock or backed by a database unique constraint /
   `INSERT ... ON CONFLICT DO NOTHING`), so that "check" and "mark as
   seen" can't be interleaved by two concurrent requests. This was
   explicitly out of scope for this exercise (no real concurrency here)
   but is worth being able to name.

5. **How would you handle an event that arrives for an order that doesn't
   exist yet, e.g. due to processing order/timing issues?**
   Strong answer worth listening for: acknowledging this is a real
   at-least-once-delivery hazard (the order-creation event and the
   payment webhook could arrive out of strict order), and discussing
   options like returning a retryable error status so the processor
   redelivers later, or holding/queuing the event for reconciliation,
   rather than silently dropping it or treating "order not found" as a
   permanent failure. There's no single required answer here — the
   exercise's `OrderNotFoundError` currently surfaces as a 404, which is
   reasonable for this exercise's scope; the interesting part is whether
   the candidate recognizes the tension between "fail fast" and "the
   processor will retry a fast-failing 4xx the same way it retries a
   5xx," and can reason about which behavior we'd actually want.

6. **Is there another valid way to implement the fix?**
   Strong answer: yes — e.g., capturing `has_seen()`'s result before
   calling `record()` and branching on it (as the reference solution
   does), or calling `record()` first and using a separate mechanism to
   detect "this call to `record()` was for an event_id already in the
   set" (functionally equivalent, since `has_seen`/`record` don't have to
   run in a fixed order relative to each other — only the *effects* gate
   has to run at most once per event_id). Any implementation preserving
   "effects apply at most once per event_id, duplicates still get logged"
   is acceptable.

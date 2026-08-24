# Bug Design (private — do not expose to candidate)

## Seed data (for reference while reading the tests)

`OrderRepository` seeds three orders, all starting `status="pending"`,
`amount_paid_cents=0`: order 101, order 102, order 103. None are special —
any of them can be used as "a fresh order" or "the order that receives a
split payment" depending on the test.

## Expected behavior

A `POST /webhooks/payment` delivery whose `status` is `"succeeded"` must
add its `amount_cents` to the order's `amount_paid_cents`, mark the order
`"paid"`, and trigger fulfillment for that order — **exactly once per
distinct `event_id`**, no matter how many times that `event_id` is
delivered. A `"failed"` event never touches the order or fulfillment. Every
delivery attempt, including exact duplicates, must still appear in the
audit log (`EventLogRepository`) — the log is a record of what the
processor sent us, not a record of what we acted on.

Two invariants must both hold simultaneously:
1. **Idempotency by event_id:** redelivering the same `event_id` must not
   reapply its effects.
2. **Independence of distinct events:** a different `event_id` for the same
   order (e.g. a second installment of a split payment) is a real, separate
   payment and must be applied normally — it is not a duplicate just
   because the order already has a successful payment on it.

## Actual (buggy) behavior

`app/services/payment_webhook_service.py::PaymentWebhookService.handle_payment_event`
never calls `self._event_log.has_seen(event.event_id)` anywhere. It calls
`self._event_log.record(event)` (correctly logging every attempt,
including duplicates) but nothing gates the business effects on whether
this exact `event_id` was already processed. So every delivery of a
`"succeeded"` event — including an exact retry of an `event_id` already
applied — increments `order.amount_paid_cents` again and calls
`fulfillment_client.fulfill(order.id)` again.

```python
def handle_payment_event(self, event: PaymentEventIn) -> dict:
    self._event_log.record(event)
    order = self._order_repository.get(event.order_id)
    if order is None:
        raise OrderNotFoundError(event.order_id)
    if event.status == "succeeded":
        order.amount_paid_cents += event.amount_cents
        order.status = "paid"
        self._order_repository.save(order)
        self._fulfillment.fulfill(order.id)
    return {"received": True}
```

## Root cause

Missing-check bug, not a broken-check bug: `EventLogRepository.has_seen`
already exists, is already correct, and is simply never called by the
service. The repository is fully functional (`has_seen` and `record` both
work exactly as documented) — the bug is entirely that the service layer
never consults `has_seen` before applying effects. This is the same *shape*
of bug as Project 7's `can_manage_document` (a correct, more-specific
helper exists on the repository and the service calls a different one
instead) generalized one step further: here the service doesn't call the
*wrong* method, it doesn't call the relevant method **at all**.

## Violated invariant

"The business effects of a given `event_id` — updating the order,
triggering fulfillment — must be applied at most once, no matter how many
times that `event_id` is delivered." (Stated in the candidate README's
Scenario and Task sections, and directly reproduced by the bug report.)

## Relevant execution path

`POST /webhooks/payment` (`app/api/routes/payments.py`) →
`PaymentWebhookService.handle_payment_event`
(`app/services/payment_webhook_service.py`, the bug) →
`EventLogRepository.has_seen` / `.record`
(`app/repositories/event_log_repository.py`, correct, both methods present
and functional but `has_seen` is unused) → `OrderRepository.get` / `.save`
(`app/repositories/order_repository.py`, correct) →
`FulfillmentClient.fulfill` (`app/clients/fulfillment_client.py`, correct
— a fake client that just records calls made to it).

## Evidence available to the candidate

- The failing public test
  `test_payment_webhook_service.py::test_duplicate_event_id_delivered_twice_applies_only_once`
  reproduces the exact reported scenario: the same `event_id` delivered
  twice, `amount_paid_cents` doubled, `fulfillment.calls` has two entries
  instead of one.
- The README states the idempotency requirement explicitly, both in the
  Scenario (at-least-once delivery background) and the Task section.
- Reading `payment_webhook_service.py` end-to-end shows `record()` is
  called but `has_seen()` never appears anywhere in the file.
- Reading `event_log_repository.py` shows `has_seen(event_id)` already
  exists, is already correctly implemented, and its docstring describes
  exactly the check that's missing from the service.
- The passing public test
  `test_two_distinct_events_apply_as_separate_partial_payments` establishes
  that the legitimate split-payment case already works on the buggy code —
  this rules out "the service never allows more than one payment per
  order" as the shape of a fix, and points specifically at *event_id*-level
  dedup rather than *order*-level dedup.

## Reasonable hypotheses

1. (Correct) The service never checks `event_log.has_seen(event_id)`
   before applying effects — there is no dedup gate at all.
2. (Plausible, wrong) Maybe `EventLogRepository.has_seen` or `record` is
   itself buggy (e.g. `has_seen` always returns `False`, or `record`
   doesn't actually persist entries). Ruled out by reading
   `event_log_repository.py`: both methods are short, correct, and
   trivially inspectable — `has_seen` checks set membership, `record` adds
   to the set and appends to the log, unconditionally.
3. (Plausible, wrong) Maybe the fake `FulfillmentClient` itself doesn't
   dedupe and that's "the bug." Ruled out because the client isn't
   supposed to dedupe anything — it's an honest recorder; deduping is a
   business-logic responsibility that belongs in the service, one layer up.
4. (Plausible, tempting, wrong — see below) Dedupe by checking
   `order.status == "paid"` instead of checking the event_id specifically.

## Intended regression tests

`test_duplicate_event_id_delivered_twice_applies_only_once` (already
present as a public test, service-level) plus hidden tests covering: three
or more redeliveries of the same event_id; the order-status-gate trap's two
distinct failure modes (below); and fulfillment-call-count correctness
across a mixed sequence of new/duplicate/failed events (see
`hidden_tests/`).

## Acceptable fixes

- Check `self._event_log.has_seen(event.event_id)` before applying the
  order update and fulfillment call; if already seen, skip those effects
  and return early. `record()` should still run for every delivery
  (including this one) — either before or after the `has_seen` check, the
  candidate's choice, as long as duplicates still get logged for audit
  purposes.
- Equivalent: capture `already_processed = has_seen(event_id)` before
  calling `record()`, then gate the effects on `not already_processed`
  (this is what `reference_solution/payment_webhook_service.py` does — it
  calls `record()` unconditionally, but decides whether to apply effects
  based on the `has_seen` result captured *before* that `record()` call).
- Not required, and out of scope for this exercise: any atomic
  check-and-set primitive, locking, or other concurrency-safety mechanism.
  `has_seen` then `record` as two separate, non-atomic calls is fine here
  — see `DEBRIEF.md` for why a genuinely concurrent version would need
  more, as a discussion-only point, not a graded requirement.

## Tempting but incomplete/wrong fix

Dedupe by checking `order.status == "paid"` (i.e., "if this order has
already been marked paid, skip") **instead of** checking the specific
`event_id`:

```python
def handle_payment_event(self, event: PaymentEventIn) -> dict:
    order = self._order_repository.get(event.order_id)
    if order is None:
        raise OrderNotFoundError(event.order_id)

    if order.status == "paid":
        return {"received": True}

    self._event_log.record(event)

    if event.status == "succeeded":
        order.amount_paid_cents += event.amount_cents
        order.status = "paid"
        self._order_repository.save(order)
        self._fulfillment.fulfill(order.id)

    return {"received": True}
```

This looks like it solves the reported symptom — after the first
`"succeeded"` event, `order.status == "paid"`, so a literal retry of that
delivery is skipped, and the originally-failing public duplicate-retry test
now passes. It is wrong in two independent ways:

1. **Blocks legitimate additional payments.** It dedupes at the *order*
   level, not the *event* level, so a second, genuinely different
   `event_id` representing a real additional (e.g. split/partial) payment
   for an already-paid order is incorrectly skipped too — the order never
   receives its second payment. This is caught by the **public** test
   `test_two_distinct_events_apply_as_separate_partial_payments` (which
   this exact tempting fix also breaks, not only the hidden tests — see
   Validated below) and by the hidden
   `test_second_distinct_event_for_same_order_is_not_blocked_by_first`
   (same class of scenario, different order/event_ids, so a fix narrowly
   tailored to the public test's exact IDs doesn't accidentally pass it).
2. **Breaks audit-trail completeness.** As written above, the early
   `return` on `order.status == "paid"` happens *before* `record()`, so a
   duplicate delivery never gets logged at all — the audit trail silently
   loses evidence that a retry was ever attempted. Caught by the hidden
   `test_duplicate_delivery_is_still_recorded_in_audit_log`. (A candidate
   could in principle move `record()` before the gate and only break
   failure mode 1 — still wrong, still caught by the tests in failure mode
   1 above.)

**Validated:** applying this exact tempting-but-incomplete
`PaymentWebhookService` to a temporary copy of the candidate repository,
with `hidden_tests/test_payment_webhook_hidden.py` copied in, and running
`pytest -q`, produced **4 failed, 9 passed** — the failures were exactly
`test_two_distinct_events_apply_as_separate_partial_payments` (public),
`test_second_distinct_event_for_same_order_is_not_blocked_by_first`
(hidden), `test_duplicate_delivery_is_still_recorded_in_audit_log`
(hidden), and `test_fulfillment_call_count_matches_distinct_successful_events`
(hidden, since the blocked second payment for order 102 in that mixed
sequence never gets a fulfillment call while the arithmetic elsewhere
still doesn't line up). The originally-failing public
`test_duplicate_event_id_delivered_twice_applies_only_once` passed, as
expected — this "fix" does solve the literal reported symptom while
breaking the broader invariant.

## Why this is interview-appropriate

Idempotent webhook/event handling — "at-least-once delivery means you must
dedupe by a stable event identifier, not by inferring 'have I already done
this' from mutable downstream state" — is one of the most common real
backend interview topics and one of the most common real-world production
bug classes (Stripe, PayPal, and most webhook-based integrations document
this exact requirement). The trap fix (gating on `order.status` instead of
`event_id`) mirrors a mistake real engineers make: reaching for "check if
the effect already happened" instead of "check if this exact cause was
already processed," which silently breaks the legitimate multi-event case.
No specialist knowledge required — fully discoverable from the code, the
failing test, and the README's stated at-least-once-delivery background.

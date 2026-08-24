# Expected Reasoning Path

1. Run `pytest -q`; observe
   `test_duplicate_event_id_delivered_twice_applies_only_once` fails while
   everything else (including
   `test_two_distinct_events_apply_as_separate_partial_payments`) passes.
2. Read the failing assertion: the same `event_id` was delivered twice via
   `service.handle_payment_event(event)` called twice with the identical
   `PaymentEventIn`, and `amount_paid_cents` came out doubled (8000 instead
   of 4000); `fulfillment.calls` would show two entries instead of one.
3. Note that the *other* multi-event test passes — two *different*
   `event_id`s for the same order both apply correctly. This is an
   important early clue: whatever's wrong, it isn't "the service refuses a
   second payment on an order" — it's specifically about redelivering the
   *same* `event_id`.
4. Open `app/services/payment_webhook_service.py`, read
   `handle_payment_event` end-to-end. Notice it calls
   `self._event_log.record(event)` but never calls anything resembling a
   "have I seen this before" check.
5. Open `app/repositories/event_log_repository.py` and notice
   `has_seen(event_id)` already exists, is short and clearly correct (set
   membership check), and is never referenced anywhere in
   `payment_webhook_service.py`.
6. Cross-check against the README's stated at-least-once-delivery
   background: "processing the same event_id twice must never apply its
   effects twice."
7. Add a gate: before applying the order update and fulfillment call,
   check `self._event_log.has_seen(event.event_id)`; skip those effects
   (but still call `record()`, so the audit trail stays complete) if
   already seen.
8. Re-run tests; the previously-failing test now passes. Manually reason
   through (or write a test for) the split-payment case again to confirm
   the fix didn't accidentally start gating on the order instead of the
   event — a strong candidate explicitly checks this, since it's the
   natural way to break rule 2 while fixing rule 1.
9. Explain: the fix restores "dedupe by the stable identifier the
   processor uses to mean 'this exact event,'" not "dedupe by inferring
   from mutable order state that this must already be handled" — those are
   different things, and only the former survives the legitimate
   split-payment scenario.

A strong candidate reaches step 7 within 20-30 minutes given the failing
test and the two repository files to read. A candidate who instead reaches
for `order.status == "paid"` as the dedup signal (skipping straight past
`EventLogRepository` without reading it closely) will pass the given
public test but should be caught by their own testing (or the hidden
tests) once they check the split-payment scenario against their fix — this
is exactly the kind of self-verification the exercise is designed to
reward.

# Payment Webhook Handler — Missing Idempotency Check (Interview Exercise)

**Format:** Advanced AI-Assisted Debugging Assessment
**Timebox:** 60–90 minutes
**Level:** Backend / Mid-level+
**Difficulty:** 8/10

## Scenario

You've just joined the payments team. This internal service receives
webhook notifications from a payment processor confirming that a customer's
payment on an order has succeeded (or failed), and — on success — triggers
order fulfillment. It's a small internal service — you haven't seen this
code before today. (The payment processor itself is simulated in this
exercise; nothing here makes a real network call.)

Payment processors commonly use **at-least-once webhook delivery**: if the
processor doesn't receive a fast, successful acknowledgement from us for a
given delivery, it will retry delivering an event with the *same*
`event_id` later. This is documented, expected behavior on the processor's
end, not a bug on their side — a correct handler on our end has to be
**idempotent**: processing the same `event_id` twice must never apply that
event's effects twice.

Separately, orders can legitimately receive **more than one** successful
payment event over their lifetime — for example, a customer paying in two
installments (a split/partial payment). Each of those is a genuinely
different `event_id` and represents a real, separate payment that must be
applied. Any fix here has to tell those two situations apart: "the same
event redelivered" vs. "a different event for the same order."

### Bug report

> "Our payment processor retries a webhook delivery if it doesn't get a
> fast enough acknowledgement from us — this is documented, expected
> behavior on their end. We just found an order that got marked as paid
> for double the correct amount, and our fulfillment system tried to ship
> it twice, after what should have been a single successful payment
> event."

## Your task

1. Reproduce the reported bug.
2. Find the root cause.
3. Fix it so that processing the same `event_id` more than once never
   applies its effects more than once — while still correctly applying
   two genuinely different `event_id`s for the same order (e.g. a split
   payment).
4. Add or strengthen tests so this can't silently regress.
5. Make sure you haven't broken any other existing behavior.

You do **not** need to add any new features — this is a bug fix only. You
also do **not** need to build a concurrency-safe (atomic check-and-set)
mechanism — there's no real concurrency in this exercise. You should,
however, be ready to discuss what a fully concurrent, multi-worker version
would additionally need.

## Repository layout

```
app/
  main.py                                FastAPI app entrypoint
  api/deps.py                            Shared repository/client/service instances
  api/routes/payments.py                 POST /webhooks/payment
  models/schemas.py                      Request/response Pydantic models
  services/payment_webhook_service.py    Webhook processing business logic
  repositories/order_repository.py       In-memory orders
  repositories/event_log_repository.py   In-memory log of webhook delivery attempts
  clients/fulfillment_client.py          Fake fulfillment client (records calls, no real I/O)
tests/
  test_payment_webhook_service.py        Unit tests for the webhook service
  test_payments_api.py                   API-level tests
```

## Setup

```bash
pip install -e ".[dev]"
```

## Running tests

```bash
pytest -q
```

One test currently fails — it encodes the reported bug. The rest pass and
describe behavior you must **not** break.

## Constraints

- Keep changes scoped to fixing this bug (plus any tests you add). Don't
  refactor unrelated code.
- Preserve the existing public API (`POST /webhooks/payment` request/
  response shape).
- Don't add a real database or make real network calls — the repositories
  and fulfillment client stay in-memory / fake.
- You don't need to build a new atomic check-and-set primitive from
  scratch for this exercise — there's no real concurrency here.

## AI tool policy

You may use an AI coding assistant. If you'd like it to behave the way a
real interview/OA proctor would configure it, load
`.ai/assessment-skill/SKILL.md` into your assistant as a system/project
instruction. It's written to work with any capable coding assistant, not
a specific product.

Using an assistant well is part of what's being evaluated — treat it like
a knowledgeable but junior pair programmer, not an oracle. You're expected
to reproduce the bug, form your own hypotheses, and verify anything it
suggests before you rely on it.

## Deliverables

- Your code fix.
- Any tests you added or changed.
- Be ready to explain: what the root cause was, how you found it, why your
  fix is correct, and what else you checked to make sure nothing else
  broke (in particular, that a legitimate second payment for the same
  order still applies correctly).
- Be ready to discuss, as a design question: what would a fully concurrent
  (multi-worker) version of this handler additionally need beyond what you
  built, and why?

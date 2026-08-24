# Evaluator Guide — Project 9: Payment Webhook Handler

## Format & target
Advanced AI-Assisted Debugging Assessment. Backend / Mid-level+. ~60-90 min.
Difficulty 8/10.

## How to grade

1. Read the candidate's diff to `app/services/payment_webhook_service.py`
   (and any other files they touched — flag if they touched unrelated
   files, e.g. `event_log_repository.py`, `fulfillment_client.py`, or the
   route).
2. Copy `hidden_tests/test_payment_webhook_hidden.py` into
   `candidate/tests/` and run `pytest -q` from `candidate/`. All public +
   hidden tests should pass for a fully correct fix.
3. Compare their fix against
   `reference_solution/payment_webhook_service.py` and `bug_design.md`'s
   "Acceptable fixes" section — several phrasings are fine, only the
   semantics matter (dedup keyed by `event_id`, duplicates still logged).
4. Read `expected_reasoning.md` and compare against the candidate's
   explanation (verbal or written) of root cause and verification,
   especially whether they explicitly checked the split-payment case.
5. Score with `scoring_rubric.md`.
6. Ask 2-3 questions from `DEBRIEF.md`.

## Interview-realism audit (private)

1. **Format simulated:** Advanced AI-assisted debugging OA / mid-level
   backend debugging interview.
2. **Role level:** Mid-level+ backend (advanced tier of this curriculum;
   first project of the "advanced interview debugging" pair alongside
   Project 10).
3. **Why feasible in 60-90 min:** Single-method root cause in one service
   file, three small supporting files (two correct repositories, one
   correct fake client), one clear failing test that reproduces the bug,
   and a second passing test that constrains the shape of the fix. A
   candidate who reads the service function and the event log repository
   side by side should locate it in 15-25 minutes, leaving time to fix,
   test the split-payment edge case explicitly, and explain.
4. **Signal obtained:** Whether the candidate can recognize an
   idempotency/event-dedup requirement from a plain-English bug report
   plus a documented delivery-semantics detail (at-least-once), correctly
   distinguish "redelivery of the same event" from "a new event that
   happens to arrive for an already-affected resource," and produce a
   minimal correct fix without breaking the legitimate multi-event case.
5. **Coding vs. reasoning split:** ~25% coding (a small conditional +
   maybe a test), ~75% reasoning/verification — slightly more
   reasoning-heavy than Project 1, appropriate for the advanced tier.
6. **Would a top company use a close variant:** Yes — "webhook handler
   isn't idempotent, processor retries caused a double charge / double
   shipment" is an extremely common real-world backend interview and
   real-world incident shape (Stripe, PayPal, and most webhook-based
   payment integrations document at-least-once delivery explicitly for
   this reason).
7. **Anything included for production education rather than signal?** The
   README's explanation of at-least-once delivery is included because a
   candidate cannot be expected to already know payment-processor delivery
   semantics as trivia — it's necessary scenario setup, not a hint at the
   fix (it establishes *why* redelivery happens, not *where* the missing
   check is).

## AI-trivialization check

Tested prompt: "Inspect this repository, run the tests, identify the
defect, and fix it." A capable general-purpose coding agent with full repo
access (not bound by the assessment SKILL.md) can plausibly solve this in
one shot: the failing test's assertion (amount doubled, fulfillment called
twice) combined with a one-file service and an unused `has_seen` method
sitting right next to the `record()` call that *is* used is a strong,
localized signal.

This is expected and acceptable for a project at this tier — the interview
signal is not "can the AI find it" but "can the candidate direct their
assistant well, distinguish a correct fix from the tempting
order-status-gate trap, verify against the split-payment invariant, and
explain the difference between event-identity dedup and state-based
dedup." Under the assessment SKILL.md, the assistant is constrained not to
just hand over the diff, which restores the intended signal: the candidate
still has to drive reproduction, hypothesis confirmation, and — critically
for this project — verification that their fix doesn't regress the
split-payment case, which is exactly where the tempting wrong fix fails.
See `ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's diff, tests, and explanation only.

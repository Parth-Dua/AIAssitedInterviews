"""Hidden tests. Copy this file into candidate/tests/ (it is not present in
the candidate repo) and run `pytest` from candidate/ after applying a
candidate's fix, or after applying
reference_solution/payment_webhook_service.py to validate the answer key.
"""

from app.models.schemas import PaymentEventIn
from app.repositories.event_log_repository import EventLogRepository
from app.repositories.order_repository import OrderRepository
from app.clients.fulfillment_client import FulfillmentClient
from app.services.payment_webhook_service import PaymentWebhookService


def make_service():
    order_repository = OrderRepository()
    event_log = EventLogRepository()
    fulfillment_client = FulfillmentClient()
    service = PaymentWebhookService(order_repository, event_log, fulfillment_client)
    return service, order_repository, event_log, fulfillment_client


def test_same_event_id_delivered_three_times_applies_only_once():
    service, orders, _, fulfillment = make_service()
    event = PaymentEventIn(
        event_id="evt-triple", order_id=101, amount_cents=1500, status="succeeded"
    )

    service.handle_payment_event(event)
    service.handle_payment_event(event)
    service.handle_payment_event(event)

    order = orders.get(101)
    assert order.amount_paid_cents == 1500
    assert fulfillment.calls == [101]


def test_second_distinct_event_for_same_order_is_not_blocked_by_first():
    """Catches the tempting-but-wrong 'skip if order.status == paid' fix:
    that gate wrongly blocks a second, genuinely different event_id
    representing a real additional (split/partial) payment, because it
    checks order state instead of the specific event_id that was already
    processed.
    """
    service, orders, _, fulfillment = make_service()
    first = PaymentEventIn(
        event_id="evt-hidden-split-1",
        order_id=102,
        amount_cents=1000,
        status="succeeded",
    )
    second = PaymentEventIn(
        event_id="evt-hidden-split-2",
        order_id=102,
        amount_cents=2500,
        status="succeeded",
    )

    service.handle_payment_event(first)
    service.handle_payment_event(second)

    order = orders.get(102)
    assert order.amount_paid_cents == 3500, (
        "a second, distinct event_id for the same order is a legitimate "
        "additional payment and must be applied, not skipped just because "
        "the order is already marked paid"
    )
    assert fulfillment.calls == [102, 102]


def test_duplicate_delivery_is_still_recorded_in_audit_log():
    """Catches an 'order.status == paid' gate implemented so that it also
    skips calling record() for a duplicate delivery. The audit log must
    show every delivery attempt the processor made, including retries
    whose effects weren't reapplied.
    """
    service, orders, event_log, fulfillment = make_service()
    event = PaymentEventIn(
        event_id="evt-hidden-audit", order_id=103, amount_cents=2000, status="succeeded"
    )

    service.handle_payment_event(event)
    service.handle_payment_event(event)

    entries = event_log.entries_for_event("evt-hidden-audit")
    assert len(entries) == 2, (
        "both delivery attempts for this event_id must appear in the audit "
        "log, even though the second one's effects were not reapplied"
    )
    order = orders.get(103)
    assert order.amount_paid_cents == 2000
    assert fulfillment.calls == [103]


def test_fulfillment_call_count_matches_distinct_successful_events():
    """Across a mixed sequence of new, duplicate, and failed events, the
    fulfillment client must be called exactly once per distinct
    successfully-applied event_id — no more, no less.
    """
    service, orders, _, fulfillment = make_service()
    events = [
        PaymentEventIn(
            event_id="evt-mix-1", order_id=101, amount_cents=1000, status="succeeded"
        ),
        PaymentEventIn(
            event_id="evt-mix-1", order_id=101, amount_cents=1000, status="succeeded"
        ),  # retry of evt-mix-1
        PaymentEventIn(
            event_id="evt-mix-2", order_id=101, amount_cents=500, status="failed"
        ),
        PaymentEventIn(
            event_id="evt-mix-3", order_id=102, amount_cents=2000, status="succeeded"
        ),
        PaymentEventIn(
            event_id="evt-mix-3", order_id=102, amount_cents=2000, status="succeeded"
        ),  # retry of evt-mix-3
        PaymentEventIn(
            event_id="evt-mix-4", order_id=102, amount_cents=750, status="succeeded"
        ),
    ]

    for event in events:
        service.handle_payment_event(event)

    # distinct successfully-applied event_ids: evt-mix-1, evt-mix-3, evt-mix-4
    assert len(fulfillment.calls) == 3
    assert fulfillment.calls.count(101) == 1
    assert fulfillment.calls.count(102) == 2
    assert orders.get(101).amount_paid_cents == 1000
    assert orders.get(102).amount_paid_cents == 2750

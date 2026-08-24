import pytest

from app.clients.fulfillment_client import FulfillmentClient
from app.models.schemas import PaymentEventIn
from app.repositories.event_log_repository import EventLogRepository
from app.repositories.order_repository import OrderRepository
from app.services.payment_webhook_service import (
    OrderNotFoundError,
    PaymentWebhookService,
)


def make_service():
    order_repository = OrderRepository()
    event_log = EventLogRepository()
    fulfillment_client = FulfillmentClient()
    service = PaymentWebhookService(order_repository, event_log, fulfillment_client)
    return service, order_repository, event_log, fulfillment_client


def test_successful_event_updates_order_and_triggers_fulfillment():
    service, orders, _, fulfillment = make_service()
    event = PaymentEventIn(
        event_id="evt-1", order_id=101, amount_cents=5000, status="succeeded"
    )

    service.handle_payment_event(event)

    order = orders.get(101)
    assert order.amount_paid_cents == 5000
    assert order.status == "paid"
    assert fulfillment.calls == [101]


def test_event_for_unknown_order_raises():
    service, *_ = make_service()
    event = PaymentEventIn(
        event_id="evt-2", order_id=9999, amount_cents=1000, status="succeeded"
    )

    with pytest.raises(OrderNotFoundError):
        service.handle_payment_event(event)


def test_failed_event_does_not_mark_order_paid_or_trigger_fulfillment():
    service, orders, _, fulfillment = make_service()
    event = PaymentEventIn(
        event_id="evt-3", order_id=102, amount_cents=3000, status="failed"
    )

    service.handle_payment_event(event)

    order = orders.get(102)
    assert order.amount_paid_cents == 0
    assert order.status == "pending"
    assert fulfillment.calls == []


def test_two_distinct_events_apply_as_separate_partial_payments():
    """A customer paying in two installments: two separate event_ids, both
    "succeeded", for the same order. This is a legitimate, intentional
    business scenario (split/partial payments) — both events must apply
    and the amounts must sum.
    """
    service, orders, _, fulfillment = make_service()
    first = PaymentEventIn(
        event_id="evt-split-1", order_id=103, amount_cents=2000, status="succeeded"
    )
    second = PaymentEventIn(
        event_id="evt-split-2", order_id=103, amount_cents=3000, status="succeeded"
    )

    service.handle_payment_event(first)
    service.handle_payment_event(second)

    order = orders.get(103)
    assert order.amount_paid_cents == 5000
    assert fulfillment.calls == [103, 103]


def test_duplicate_event_id_delivered_twice_applies_only_once():
    """Bug report: the payment processor retries a webhook delivery if it
    doesn't get a fast enough acknowledgement from us — documented,
    expected behavior on their end. We found an order marked paid for
    double the correct amount, and fulfillment tried to ship it twice,
    after what should have been a single successful payment event.
    """
    service, orders, _, fulfillment = make_service()
    event = PaymentEventIn(
        event_id="evt-retry", order_id=101, amount_cents=4000, status="succeeded"
    )

    service.handle_payment_event(event)
    service.handle_payment_event(event)

    order = orders.get(101)
    assert order.amount_paid_cents == 4000, (
        "the same event_id was delivered twice (a processor retry); its "
        "effects must be applied only once"
    )
    assert fulfillment.calls == [101]

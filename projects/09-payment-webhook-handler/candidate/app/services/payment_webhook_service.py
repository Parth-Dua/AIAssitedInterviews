from app.clients.fulfillment_client import FulfillmentClient
from app.models.schemas import PaymentEventIn
from app.repositories.event_log_repository import EventLogRepository
from app.repositories.order_repository import OrderRepository


class OrderNotFoundError(Exception):
    pass


class PaymentWebhookService:
    """Applies incoming payment webhook events to orders and triggers
    fulfillment.

    Business rules:
      1. A "succeeded" event adds its amount_cents to the order's
         amount_paid_cents and marks the order "paid", then triggers
         fulfillment for that order.
      2. An order can legitimately receive more than one "succeeded" event
         over its lifetime (e.g. a customer paying in two installments) —
         each distinct event_id represents a real, separate payment and
         must be applied.
      3. The payment processor uses at-least-once delivery: it may redeliver
         the exact same event_id more than once. Processing the same
         event_id more than once must never apply its effects (the order
         update, the fulfillment call) more than once.
      4. A "failed" event never updates the order and never triggers
         fulfillment.
    """

    def __init__(
        self,
        order_repository: OrderRepository,
        event_log: EventLogRepository,
        fulfillment_client: FulfillmentClient,
    ):
        self._order_repository = order_repository
        self._event_log = event_log
        self._fulfillment = fulfillment_client

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

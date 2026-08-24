"""Wires up the (in-memory) repositories, clients, and services shared
across routers. There's no database or DI framework here, so this module
just owns the singleton instances every route depends on.
"""

from app.clients.fulfillment_client import FulfillmentClient
from app.repositories.event_log_repository import EventLogRepository
from app.repositories.order_repository import OrderRepository
from app.services.payment_webhook_service import PaymentWebhookService

order_repository = OrderRepository()
event_log_repository = EventLogRepository()
fulfillment_client = FulfillmentClient()

payment_webhook_service = PaymentWebhookService(
    order_repository, event_log_repository, fulfillment_client
)

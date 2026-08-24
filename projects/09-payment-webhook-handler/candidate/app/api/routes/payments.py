from fastapi import APIRouter, HTTPException

from app.api.deps import payment_webhook_service
from app.models.schemas import PaymentEventIn, PaymentWebhookResponse
from app.services.payment_webhook_service import OrderNotFoundError

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/payment", response_model=PaymentWebhookResponse)
def receive_payment_webhook(event: PaymentEventIn) -> PaymentWebhookResponse:
    """Receives a webhook delivery from the payment processor confirming
    (or failing) a payment on an order, and triggers fulfillment on
    success. The processor may redeliver the same event_id more than once.
    """
    try:
        result = payment_webhook_service.handle_payment_event(event)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="order not found")
    return PaymentWebhookResponse(**result)

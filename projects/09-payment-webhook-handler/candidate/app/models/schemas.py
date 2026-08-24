from typing import Literal

from pydantic import BaseModel, Field


class PaymentEventIn(BaseModel):
    """A single webhook delivery from the payment processor.

    `event_id` uniquely identifies one underlying payment event on the
    processor's side. The processor uses at-least-once delivery: if it
    doesn't receive a fast, successful acknowledgement from us, it will
    retry delivering an event with the *same* `event_id` later.
    """

    event_id: str
    order_id: int
    amount_cents: int = Field(gt=0)
    status: Literal["succeeded", "failed"]


class PaymentWebhookResponse(BaseModel):
    received: bool


class Order(BaseModel):
    id: int
    status: str
    amount_paid_cents: int

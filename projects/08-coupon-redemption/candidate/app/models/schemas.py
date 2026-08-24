from typing import Optional

from pydantic import BaseModel, Field


class CouponOut(BaseModel):
    """Public representation of a coupon's current, persisted state."""

    code: str
    discount_type: str
    percent_value: Optional[float] = None
    fixed_amount_cents: Optional[int] = None
    max_redemptions: int
    redemption_count: int
    status: str


class ApplyDiscountRequest(BaseModel):
    """Request body for pricing an order subtotal against a coupon."""

    subtotal_cents: int = Field(ge=0)


class ApplyDiscountResponse(BaseModel):
    subtotal_cents: int
    total_cents: int

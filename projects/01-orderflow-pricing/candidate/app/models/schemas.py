from typing import List, Optional

from pydantic import BaseModel, Field


class LineItemIn(BaseModel):
    sku: str
    unit_price_cents: int = Field(gt=0)
    quantity: int = Field(gt=0)


class PriceOrderRequest(BaseModel):
    items: List[LineItemIn]
    discount_code: Optional[str] = None


class PriceBreakdown(BaseModel):
    subtotal_cents: int
    discount_cents: int
    shipping_cents: int
    total_cents: int

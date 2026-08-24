from typing import List, Optional

from pydantic import BaseModel, Field


class Reservation(BaseModel):
    """A single reservation: units of a SKU set aside against an outgoing
    order.

    `sequence` is a monotonically increasing integer assigned when the
    reservation was created. It plays the role a real `created_at`
    timestamp would play for ordering and cursor pagination, but stays a
    plain integer so tests are deterministic.
    """

    id: int
    sku: str
    category: str
    quantity: int = Field(gt=0)
    status: str
    sequence: int


class ReservationPage(BaseModel):
    items: List[Reservation]
    next_cursor: Optional[int] = None

from dataclasses import dataclass
from typing import Optional


@dataclass
class Coupon:
    """A promo coupon and its redemption state.

    `discount_type` is either `"percentage"` or `"fixed_amount"`. Exactly one
    of `percent_value` / `fixed_amount_cents` is populated, matching
    `discount_type` — the other stays `None`. `status` is one of `"active"`,
    `"exhausted"`, or `"cancelled"`.
    """

    code: str
    discount_type: str
    max_redemptions: int
    percent_value: Optional[float] = None
    fixed_amount_cents: Optional[int] = None
    redemption_count: int = 0
    status: str = "active"

import copy

from app.domain.coupon import Coupon


class CouponRepository:
    """In-memory store of coupons, keyed by code.

    `save` and `get_by_code` both hand back defensive copies rather than the
    live stored instance, so callers never hold a reference to
    repository-owned state.
    """

    def __init__(self):
        self._coupons: dict[str, Coupon] = {}
        for coupon in _seed_coupons():
            self._coupons[coupon.code] = copy.deepcopy(coupon)

    def get_by_code(self, code: str) -> Coupon | None:
        stored = self._coupons.get(code)
        if stored is None:
            return None
        return copy.deepcopy(stored)

    def save(self, coupon: Coupon) -> Coupon:
        self._coupons[coupon.code] = copy.deepcopy(coupon)
        return copy.deepcopy(self._coupons[coupon.code])

    def list_all(self) -> list[Coupon]:
        return [copy.deepcopy(c) for c in self._coupons.values()]


def _seed_coupons() -> list[Coupon]:
    return [
        Coupon(
            code="WELCOME10",
            discount_type="percentage",
            max_redemptions=100,
            percent_value=10.0,
        ),
        Coupon(
            code="SAVE5",
            discount_type="fixed_amount",
            max_redemptions=50,
            fixed_amount_cents=500,
        ),
        Coupon(
            code="BIGDISCOUNT",
            discount_type="fixed_amount",
            max_redemptions=10,
            fixed_amount_cents=2000,
        ),
        Coupon(
            code="RETIRED",
            discount_type="percentage",
            max_redemptions=10,
            percent_value=15.0,
            status="cancelled",
        ),
        Coupon(
            code="LOYALTY3",
            discount_type="percentage",
            max_redemptions=3,
            percent_value=20.0,
        ),
        Coupon(
            code="LOYALTY2",
            discount_type="percentage",
            max_redemptions=2,
            percent_value=8.0,
        ),
        Coupon(
            code="HOLIDAY2",
            discount_type="percentage",
            max_redemptions=2,
            percent_value=12.0,
        ),
    ]

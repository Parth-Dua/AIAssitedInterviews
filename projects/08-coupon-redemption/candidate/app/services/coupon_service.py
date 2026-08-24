from app.domain.coupon import Coupon
from app.repositories.coupon_repository import CouponRepository


class CouponNotFoundError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(f"coupon {code!r} not found")


class CouponNotRedeemableError(Exception):
    def __init__(self, code: str, status: str):
        self.code = code
        self.status = status
        super().__init__(f"coupon {code!r} is not redeemable (status={status!r})")


class UnsupportedDiscountTypeError(Exception):
    def __init__(self, discount_type: str):
        self.discount_type = discount_type
        super().__init__(f"unsupported discount_type {discount_type!r}")


class CouponService:
    """Coupon lookup, redemption, and discount pricing."""

    def __init__(self, repository: CouponRepository):
        self._repository = repository

    def get_coupon(self, code: str) -> Coupon:
        coupon = self._repository.get_by_code(code)
        if coupon is None:
            raise CouponNotFoundError(code)
        return coupon

    def redeem(self, code: str) -> Coupon:
        """Record one redemption against a coupon, enforcing its status and
        redemption limit.
        """
        coupon = self._repository.get_by_code(code)
        if coupon is None:
            raise CouponNotFoundError(code)
        if coupon.status != "active":
            raise CouponNotRedeemableError(code, coupon.status)
        coupon.redemption_count += 1
        self._repository.save(coupon)
        if coupon.redemption_count >= coupon.max_redemptions:
            coupon.status = "exhausted"
        return coupon

    def apply_discount(self, coupon: Coupon, subtotal_cents: int) -> int:
        """Return the discounted total, in cents, for an order subtotal."""
        if coupon.discount_type == "percentage":
            discount = round(subtotal_cents * (coupon.percent_value / 100))
            return max(subtotal_cents - discount, 0)
        raise UnsupportedDiscountTypeError(coupon.discount_type)

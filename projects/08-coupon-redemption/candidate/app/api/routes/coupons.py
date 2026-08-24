from fastapi import APIRouter, HTTPException

from app.api.deps import coupon_service
from app.domain.coupon import Coupon
from app.models.schemas import ApplyDiscountRequest, ApplyDiscountResponse, CouponOut
from app.services.coupon_service import (
    CouponNotFoundError,
    CouponNotRedeemableError,
    UnsupportedDiscountTypeError,
)

router = APIRouter(prefix="/coupons", tags=["coupons"])


def _to_out(coupon: Coupon) -> CouponOut:
    return CouponOut(
        code=coupon.code,
        discount_type=coupon.discount_type,
        percent_value=coupon.percent_value,
        fixed_amount_cents=coupon.fixed_amount_cents,
        max_redemptions=coupon.max_redemptions,
        redemption_count=coupon.redemption_count,
        status=coupon.status,
    )


@router.get("/{code}", response_model=CouponOut)
def get_coupon(code: str) -> CouponOut:
    """Return a coupon's current, persisted state."""
    try:
        coupon = coupon_service.get_coupon(code)
    except CouponNotFoundError:
        raise HTTPException(status_code=404, detail=f"coupon {code!r} not found")
    return _to_out(coupon)


@router.post("/{code}/redeem", response_model=CouponOut)
def redeem_coupon(code: str) -> CouponOut:
    """Record one redemption against a coupon."""
    try:
        coupon = coupon_service.redeem(code)
    except CouponNotFoundError:
        raise HTTPException(status_code=404, detail=f"coupon {code!r} not found")
    except CouponNotRedeemableError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return _to_out(coupon)


@router.post("/{code}/apply", response_model=ApplyDiscountResponse)
def apply_discount(code: str, request: ApplyDiscountRequest) -> ApplyDiscountResponse:
    """Price an order subtotal against a coupon, without redeeming it."""
    try:
        coupon = coupon_service.get_coupon(code)
    except CouponNotFoundError:
        raise HTTPException(status_code=404, detail=f"coupon {code!r} not found")
    try:
        total_cents = coupon_service.apply_discount(coupon, request.subtotal_cents)
    except UnsupportedDiscountTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ApplyDiscountResponse(
        subtotal_cents=request.subtotal_cents, total_cents=total_cents
    )

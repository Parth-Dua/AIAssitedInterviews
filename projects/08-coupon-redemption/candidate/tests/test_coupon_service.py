import pytest

from app.repositories.coupon_repository import CouponRepository
from app.services.coupon_service import CouponNotRedeemableError, CouponService


def make_service() -> tuple[CouponService, CouponRepository]:
    repository = CouponRepository()
    return CouponService(repository), repository


def test_redeem_increments_redemption_count_on_fresh_read():
    service, repository = make_service()

    service.redeem("WELCOME10")

    persisted = repository.get_by_code("WELCOME10")
    assert persisted.redemption_count == 1


def test_redeeming_a_cancelled_coupon_is_rejected():
    service, repository = make_service()

    with pytest.raises(CouponNotRedeemableError):
        service.redeem("RETIRED")

    persisted = repository.get_by_code("RETIRED")
    assert persisted.redemption_count == 0


def test_redeeming_beyond_max_redemptions_is_rejected():
    """LOYALTY3 has max_redemptions=3. A 4th redemption must be rejected."""
    service, _repository = make_service()

    service.redeem("LOYALTY3")
    service.redeem("LOYALTY3")
    service.redeem("LOYALTY3")

    with pytest.raises(CouponNotRedeemableError):
        service.redeem("LOYALTY3")


def test_exhausted_coupon_status_is_persisted():
    """After the max-th redemption, a fresh repository read must show the
    coupon as exhausted — not merely the in-memory object redeem() returned.
    """
    service, repository = make_service()

    service.redeem("LOYALTY2")
    service.redeem("LOYALTY2")  # LOYALTY2 has max_redemptions=2

    persisted = repository.get_by_code("LOYALTY2")
    assert persisted.status == "exhausted"


def test_apply_percentage_discount():
    service, repository = make_service()
    coupon = repository.get_by_code("WELCOME10")

    total = service.apply_discount(coupon, subtotal_cents=2000)

    assert total == 1800


def test_apply_fixed_amount_discount():
    service, repository = make_service()
    coupon = repository.get_by_code("SAVE5")

    total = service.apply_discount(coupon, subtotal_cents=2000)

    assert total == 1500

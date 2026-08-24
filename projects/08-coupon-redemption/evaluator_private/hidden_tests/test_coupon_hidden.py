"""Hidden tests. Copy this file into candidate/tests/ (it is not present in
the candidate repo) and run `pytest` from candidate/ after applying a
candidate's fix, or after applying reference_solution/coupon_service.py to
validate the answer key.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.coupon_repository import CouponRepository
from app.services.coupon_service import CouponNotRedeemableError, CouponService

client = TestClient(app)


def make_service() -> tuple[CouponService, CouponRepository]:
    repository = CouponRepository()
    return CouponService(repository), repository


def test_exhaustion_boundary_is_exact_not_off_by_one():
    """LOYALTY3 has max_redemptions=3. The 3rd redemption must exhaust it
    (persisted, visible on a fresh repository read) — not the 2nd, and not
    a 4th that should never be allowed to succeed.
    """
    service, repository = make_service()

    service.redeem("LOYALTY3")
    service.redeem("LOYALTY3")
    still_active = repository.get_by_code("LOYALTY3")
    assert still_active.redemption_count == 2
    assert still_active.status == "active"

    service.redeem("LOYALTY3")
    now_exhausted = repository.get_by_code("LOYALTY3")
    assert now_exhausted.redemption_count == 3
    assert now_exhausted.status == "exhausted"

    with pytest.raises(CouponNotRedeemableError):
        service.redeem("LOYALTY3")

    final = repository.get_by_code("LOYALTY3")
    assert final.redemption_count == 3
    assert final.status == "exhausted"


def test_redeem_exhausted_coupon_returns_409_and_does_not_increment_again():
    """API-level twin of the boundary test, using a coupon untouched by any
    other test so the shared in-process app state can't interfere. Confirms
    rejection is a clean error response, not a crash, and that the rejected
    attempt leaves redemption_count unchanged.
    """
    for _ in range(2):
        response = client.post("/coupons/HOLIDAY2/redeem")
        assert response.status_code == 200

    third = client.post("/coupons/HOLIDAY2/redeem")
    assert third.status_code == 409

    fetched = client.get("/coupons/HOLIDAY2")
    body = fetched.json()
    assert body["status"] == "exhausted"
    assert body["redemption_count"] == 2


def test_fixed_amount_discount_exceeding_subtotal_clamps_to_zero():
    """BIGDISCOUNT is a 2000-cent fixed discount. Against a 500-cent
    subtotal, the discounted total must clamp to 0, never go negative.
    """
    service, repository = make_service()
    coupon = repository.get_by_code("BIGDISCOUNT")

    total = service.apply_discount(coupon, subtotal_cents=500)

    assert total == 0


def test_percentage_discount_rounding_is_unchanged():
    """Exact-value regression guard: adding fixed_amount support must not
    change percentage-coupon arithmetic or rounding at all.
    """
    service, repository = make_service()
    coupon = repository.get_by_code("WELCOME10")  # 10% off

    assert service.apply_discount(coupon, subtotal_cents=999) == 899
    assert service.apply_discount(coupon, subtotal_cents=1000) == 900
    assert service.apply_discount(coupon, subtotal_cents=333) == 300

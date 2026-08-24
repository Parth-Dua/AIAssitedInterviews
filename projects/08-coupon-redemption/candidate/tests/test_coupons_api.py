from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_get_unknown_coupon_returns_404():
    response = client.get("/coupons/NOPE")
    assert response.status_code == 404


def test_redeem_increments_count_visible_on_a_fresh_get():
    redeem = client.post("/coupons/WELCOME10/redeem")
    assert redeem.status_code == 200

    fetched = client.get("/coupons/WELCOME10")
    assert fetched.status_code == 200
    assert fetched.json()["redemption_count"] == 1


def test_redeeming_a_cancelled_coupon_is_rejected():
    response = client.post("/coupons/RETIRED/redeem")
    assert response.status_code == 409


def test_redeeming_beyond_max_redemptions_is_rejected():
    """LOYALTY3 has max_redemptions=3. The 4th redemption must be rejected."""
    for _ in range(3):
        response = client.post("/coupons/LOYALTY3/redeem")
        assert response.status_code == 200

    fourth = client.post("/coupons/LOYALTY3/redeem")
    assert fourth.status_code == 409


def test_exhausted_coupon_status_visible_on_fresh_get():
    """LOYALTY2 has max_redemptions=2. After redeeming it out, a separate
    GET call (not the redeem response itself) must show it as exhausted.
    """
    for _ in range(2):
        response = client.post("/coupons/LOYALTY2/redeem")
        assert response.status_code == 200

    fetched = client.get("/coupons/LOYALTY2")
    assert fetched.json()["status"] == "exhausted"


def test_apply_percentage_discount_endpoint():
    response = client.post("/coupons/WELCOME10/apply", json={"subtotal_cents": 2000})
    assert response.status_code == 200
    assert response.json()["total_cents"] == 1800


def test_apply_fixed_amount_discount_endpoint():
    response = client.post("/coupons/SAVE5/apply", json={"subtotal_cents": 2000})
    assert response.status_code == 200
    assert response.json()["total_cents"] == 1500

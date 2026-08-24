from app.models.schemas import LineItemIn
from app.repositories.pricing_repository import PricingRepository
from app.services.pricing_service import PricingService


def make_service() -> PricingService:
    return PricingService(PricingRepository())


def test_subtotal_is_sum_of_line_items():
    service = make_service()
    items = [
        LineItemIn(sku="A", unit_price_cents=1000, quantity=2),
        LineItemIn(sku="B", unit_price_cents=500, quantity=1),
    ]
    breakdown = service.price_order(items)
    assert breakdown.subtotal_cents == 2500


def test_flat_shipping_charged_below_threshold():
    service = make_service()
    items = [LineItemIn(sku="A", unit_price_cents=2000, quantity=1)]
    breakdown = service.price_order(items)
    assert breakdown.shipping_cents == 499
    assert breakdown.total_cents == 2000 + 499


def test_free_shipping_above_threshold_no_discount():
    service = make_service()
    items = [LineItemIn(sku="A", unit_price_cents=6000, quantity=1)]
    breakdown = service.price_order(items)
    assert breakdown.shipping_cents == 0
    assert breakdown.total_cents == 6000


def test_discount_code_reduces_subtotal_correctly():
    service = make_service()
    items = [LineItemIn(sku="A", unit_price_cents=1000, quantity=1)]
    breakdown = service.price_order(items, discount_code="WELCOME10")
    # 10% off 1000 = 100
    assert breakdown.discount_cents == 100


def test_unknown_discount_code_is_ignored():
    service = make_service()
    items = [LineItemIn(sku="A", unit_price_cents=1000, quantity=1)]
    breakdown = service.price_order(items, discount_code="NOT-A-REAL-CODE")
    assert breakdown.discount_cents == 0


def test_free_shipping_preserved_when_discount_applied():
    """Bug report from support: 'A customer's cart subtotal was $52 (above
    our $50 free-shipping threshold) before applying the WELCOME10 promo
    code, but they were still charged the $4.99 shipping fee once the promo
    was applied.' Free shipping eligibility is supposed to be based on the
    order's subtotal *before* any discount is applied.
    """
    service = make_service()
    items = [LineItemIn(sku="A", unit_price_cents=5200, quantity=1)]
    breakdown = service.price_order(items, discount_code="WELCOME10")

    assert breakdown.subtotal_cents == 5200
    assert breakdown.discount_cents == 520
    assert breakdown.shipping_cents == 0, (
        "subtotal was above the free-shipping threshold before the discount "
        "was applied, so shipping should be free"
    )

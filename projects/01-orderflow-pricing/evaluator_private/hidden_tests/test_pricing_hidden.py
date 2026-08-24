"""Hidden tests. Copy this file into candidate/tests/ (it is not present in
the candidate repo) and run `pytest` from candidate/ after applying a
candidate's fix, or after applying reference_solution/pricing_service.py to
validate the answer key.
"""

from app.models.schemas import LineItemIn
from app.repositories.pricing_repository import PricingRepository
from app.services.pricing_service import PricingService


def make_service() -> PricingService:
    return PricingService(PricingRepository())


def test_shipping_boundary_exact_threshold_no_discount():
    service = make_service()
    items = [LineItemIn(sku="A", unit_price_cents=5000, quantity=1)]
    breakdown = service.price_order(items)
    assert breakdown.shipping_cents == 0


def test_shipping_boundary_one_cent_below_threshold():
    service = make_service()
    items = [LineItemIn(sku="A", unit_price_cents=4999, quantity=1)]
    breakdown = service.price_order(items)
    assert breakdown.shipping_cents == 499


def test_discount_amount_independent_of_shipping_outcome():
    """The discount must always be exactly percent * pre-discount subtotal,
    regardless of whether the order crosses the free-shipping threshold.
    Catches the 'cap the discount to protect free shipping' incomplete fix.
    """
    service = make_service()
    items = [LineItemIn(sku="A", unit_price_cents=5001, quantity=1)]
    breakdown = service.price_order(items, discount_code="VIP30")
    assert breakdown.discount_cents == round(5001 * 30 / 100)
    assert breakdown.shipping_cents == 0  # pre-discount subtotal qualifies


def test_large_discount_still_pre_discount_shipping_eligible():
    service = make_service()
    items = [LineItemIn(sku="A", unit_price_cents=10000, quantity=1)]
    breakdown = service.price_order(items, discount_code="VIP30")
    assert breakdown.discount_cents == 3000
    assert breakdown.shipping_cents == 0
    assert breakdown.total_cents == 10000 - 3000 + 0


def test_subtotal_genuinely_below_threshold_still_charges_shipping():
    """Guards against an overcorrection that makes shipping always free."""
    service = make_service()
    items = [LineItemIn(sku="A", unit_price_cents=1000, quantity=1)]
    breakdown = service.price_order(items, discount_code="WELCOME10")
    assert breakdown.shipping_cents == 499


def test_discount_code_case_insensitive():
    service = make_service()
    items = [LineItemIn(sku="A", unit_price_cents=1000, quantity=1)]
    breakdown = service.price_order(items, discount_code="welcome10")
    assert breakdown.discount_cents == 100


def test_total_is_internally_consistent_across_scenarios():
    service = make_service()
    cases = [
        ([LineItemIn(sku="A", unit_price_cents=5200, quantity=1)], "WELCOME10"),
        ([LineItemIn(sku="A", unit_price_cents=100, quantity=3)], None),
        ([LineItemIn(sku="A", unit_price_cents=7000, quantity=2)], "SAVE20"),
    ]
    for items, code in cases:
        breakdown = service.price_order(items, discount_code=code)
        assert (
            breakdown.total_cents
            == breakdown.subtotal_cents
            - breakdown.discount_cents
            + breakdown.shipping_cents
        )


def test_multiple_line_items_with_discount_and_free_shipping():
    service = make_service()
    items = [
        LineItemIn(sku="A", unit_price_cents=3000, quantity=1),
        LineItemIn(sku="B", unit_price_cents=2500, quantity=1),
    ]
    breakdown = service.price_order(items, discount_code="SAVE20")
    assert breakdown.subtotal_cents == 5500
    assert breakdown.discount_cents == 1100
    assert breakdown.shipping_cents == 0
    assert breakdown.total_cents == 5500 - 1100 + 0

from app.domain.constants import FLAT_SHIPPING_CENTS, FREE_SHIPPING_THRESHOLD_CENTS
from app.models.schemas import LineItemIn, PriceBreakdown
from app.repositories.pricing_repository import PricingRepository


class PricingService:
    """Computes the price breakdown for an order.

    Business rules:
      1. subtotal = sum(unit_price * quantity) across line items.
      2. If a valid discount_code is supplied, it is applied as a percentage
         off the subtotal.
      3. Orders qualify for free shipping once the order's PRE-DISCOUNT
         subtotal reaches FREE_SHIPPING_THRESHOLD_CENTS. A discount can never
         cause an order to lose free shipping it already qualified for.
      4. total = subtotal - discount + shipping.
    """

    def __init__(self, repository: PricingRepository):
        self._repository = repository

    def price_order(
        self, items: list[LineItemIn], discount_code: str | None = None
    ) -> PriceBreakdown:
        subtotal_cents = sum(item.unit_price_cents * item.quantity for item in items)

        discount_cents = 0
        if discount_code:
            percent_off = self._repository.get_discount_percent(discount_code)
            if percent_off:
                discount_cents = round(subtotal_cents * percent_off / 100)

        if subtotal_cents >= FREE_SHIPPING_THRESHOLD_CENTS:
            shipping_cents = 0
        else:
            shipping_cents = FLAT_SHIPPING_CENTS

        total_cents = subtotal_cents - discount_cents + shipping_cents

        return PriceBreakdown(
            subtotal_cents=subtotal_cents,
            discount_cents=discount_cents,
            shipping_cents=shipping_cents,
            total_cents=total_cents,
        )

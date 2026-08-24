from fastapi import APIRouter

from app.models.schemas import PriceBreakdown, PriceOrderRequest
from app.repositories.pricing_repository import PricingRepository
from app.services.pricing_service import PricingService

router = APIRouter(prefix="/orders", tags=["orders"])

_repository = PricingRepository()
_service = PricingService(_repository)


@router.post("/price", response_model=PriceBreakdown)
def price_order(request: PriceOrderRequest) -> PriceBreakdown:
    """Return the price breakdown (subtotal, discount, shipping, total) for
    a proposed order. Does not persist anything — used by the checkout page
    to show a live price preview as the customer edits their cart.
    """
    return _service.price_order(request.items, request.discount_code)

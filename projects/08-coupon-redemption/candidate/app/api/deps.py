"""Wires up the (in-memory) repository and service shared across routers.
There's no database or DI framework here, so this module just owns the
singleton instances every route depends on.
"""

from app.repositories.coupon_repository import CouponRepository
from app.services.coupon_service import CouponService

coupon_repository = CouponRepository()
coupon_service = CouponService(coupon_repository)

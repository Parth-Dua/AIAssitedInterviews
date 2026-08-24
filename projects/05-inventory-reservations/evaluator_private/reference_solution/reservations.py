from typing import Optional

from fastapi import APIRouter

from app.models.schemas import ReservationPage
from app.repositories.reservation_repository import ReservationRepository
from app.services.reservation_service import ReservationService

router = APIRouter(tags=["reservations"])

_repository = ReservationRepository()
_service = ReservationService(_repository)


@router.get("/reservations", response_model=ReservationPage)
def list_reservations(
    cursor: Optional[int] = None,
    limit: int = 10,
    category: Optional[str] = None,
) -> ReservationPage:
    """Return a page of reservations ordered by creation sequence
    ascending, optionally restricted to a single `category`. Used by the
    warehouse dashboard to page through the reservations list.
    """
    return _service.list_reservations(cursor=cursor, limit=limit, category=category)

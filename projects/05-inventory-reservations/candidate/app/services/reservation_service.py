from app.models.schemas import ReservationPage
from app.repositories.reservation_repository import ReservationRepository


class ReservationService:
    """Thin orchestration layer over ReservationRepository.

    Pagination contract: a request returns up to `limit` items starting
    just after `cursor` (or from the start if `cursor` is None). If a full
    page of `limit` items was returned, `next_cursor` is set to the last
    returned item's `sequence` so the caller can request the following
    page; otherwise (a short page) there is nothing left and `next_cursor`
    is None.
    """

    def __init__(self, repository: ReservationRepository):
        self._repository = repository

    def list_reservations(
        self,
        cursor: int | None,
        limit: int,
        category: str | None = None,
    ) -> ReservationPage:
        items = self._repository.list_page(cursor, limit)
        next_cursor = items[-1].sequence if len(items) == limit else None
        return ReservationPage(items=items, next_cursor=next_cursor)

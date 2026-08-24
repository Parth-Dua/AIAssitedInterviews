from app.repositories.reservation_repository import ReservationRepository
from app.services.reservation_service import ReservationService

TOTAL_SEEDED_RESERVATIONS = 18


def make_service() -> ReservationService:
    return ReservationService(ReservationRepository())


def test_pagination_no_duplicates_across_two_pages():
    """Bug report from the warehouse app team: 'when we paginate through
    reservations 10 at a time, the last item from page 1 also shows up as
    the first item of page 2.' Reproduced here with limit=5.
    """
    service = make_service()
    page1 = service.list_reservations(cursor=None, limit=5)
    page2 = service.list_reservations(cursor=page1.next_cursor, limit=5)

    ids_page1 = [r.id for r in page1.items]
    ids_page2 = [r.id for r in page2.items]

    assert len(ids_page1) == 5
    assert len(ids_page2) == 5

    combined = ids_page1 + ids_page2
    assert len(combined) == len(set(combined)), (
        "page 2 re-returned an item already seen on page 1 "
        f"(page1={ids_page1}, page2={ids_page2})"
    )


def test_last_page_returns_null_next_cursor():
    service = make_service()
    page = service.list_reservations(cursor=None, limit=25)
    assert len(page.items) == TOTAL_SEEDED_RESERVATIONS
    assert page.next_cursor is None


def test_limit_is_respected():
    service = make_service()
    page = service.list_reservations(cursor=None, limit=3)
    assert len(page.items) == 3


def test_items_ordered_by_sequence_ascending():
    service = make_service()
    page = service.list_reservations(cursor=None, limit=6)
    sequences = [r.sequence for r in page.items]
    assert sequences == sorted(sequences)

"""Hidden tests. Copy this file into candidate/tests/ (it is not present in
the candidate repo) and run `pytest` from candidate/ after applying a
candidate's fix, or after applying reference_solution/ to validate the
answer key.
"""

from app.repositories.reservation_repository import ReservationRepository
from app.services.reservation_service import ReservationService

TOTAL_SEEDED_RESERVATIONS = 18
ELECTRONICS_IDS = [1, 3, 6, 8, 11, 14, 17]


def make_service() -> ReservationService:
    return ReservationService(ReservationRepository())


def _collect_all(service, category=None, limit=5):
    """Page through the full (optionally filtered) result set via cursor
    until next_cursor is null, returning every item seen.
    """
    collected = []
    cursor = None
    seen_cursors: set[int] = set()
    while True:
        page = service.list_reservations(cursor=cursor, limit=limit, category=category)
        collected.extend(page.items)
        if page.next_cursor is None:
            break
        assert page.next_cursor not in seen_cursors, (
            f"cursor {page.next_cursor} repeated — pagination is not making progress "
            "(possible infinite loop)"
        )
        seen_cursors.add(page.next_cursor)
        cursor = page.next_cursor
    return collected


def test_full_traversal_no_category_collects_every_reservation_exactly_once():
    """Catches the off-by-one boundary bug under a variety of page sizes,
    including sizes that do and don't evenly divide the total.
    """
    service = make_service()
    for limit in (4, 5, 7, 100):
        collected = _collect_all(service, limit=limit)
        ids = [r.id for r in collected]
        assert len(ids) == len(set(ids)), f"duplicate ids collected with limit={limit}: {ids}"
        assert sorted(ids) == list(range(1, TOTAL_SEEDED_RESERVATIONS + 1)), (
            f"limit={limit}: expected all {TOTAL_SEEDED_RESERVATIONS} ids, got {sorted(ids)}"
        )


def test_full_traversal_with_category_filter_collects_exactly_that_categorys_items():
    """Catches the 'paginate first, then filter the page by category'
    mistake: electronics items are scattered among 18 reservations (not
    contiguous), and there are more electronics items (7) than the page
    sizes used here, so a naive implementation either returns fewer than
    `limit` items per page or terminates early and misses items.
    """
    service = make_service()
    for limit in (2, 3, 5):
        collected = _collect_all(service, category="electronics", limit=limit)
        ids = sorted(r.id for r in collected)
        assert len(ids) == len(set(ids)), f"limit={limit}: duplicate electronics ids: {ids}"
        assert ids == ELECTRONICS_IDS, (
            f"limit={limit}: expected electronics ids {ELECTRONICS_IDS}, got {ids}"
        )
        for r in collected:
            assert r.category == "electronics"


def test_limit_larger_than_remaining_items_on_last_page():
    """Reservations 16, 17, 18 are the only ones with sequence > 15. A
    limit far larger than what remains should return exactly those three
    and signal there is nothing more to page through.
    """
    service = make_service()
    page = service.list_reservations(cursor=15, limit=1000)
    assert [r.id for r in page.items] == [16, 17, 18]
    assert page.next_cursor is None


def test_category_filter_with_cursor_from_unfiltered_page_does_not_crash():
    """Edge case: a cursor obtained from an unfiltered request, then reused
    on a request that adds a category filter. Documented/expected
    behavior: cursor is a global sequence boundary ('resume after this
    sequence number'); combining it with a different filter than the one
    that produced it is well-defined and must not error — it simply
    returns matching items whose sequence is past the cursor.
    """
    service = make_service()
    unfiltered_page1 = service.list_reservations(cursor=None, limit=5)
    cursor = unfiltered_page1.next_cursor
    assert cursor == 5

    result = service.list_reservations(cursor=cursor, limit=10, category="apparel")

    assert all(r.category == "apparel" for r in result.items)
    assert all(r.sequence > cursor for r in result.items)
    # apparel sequences are 2, 7, 12, 16 — only those past sequence 5 remain
    assert [r.id for r in result.items] == [7, 12, 16]
    assert result.next_cursor is None

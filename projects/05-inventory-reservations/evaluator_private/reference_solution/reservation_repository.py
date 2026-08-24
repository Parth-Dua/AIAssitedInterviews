from app.models.schemas import Reservation


def _seed_reservations() -> list[Reservation]:
    """Sample warehouse reservations, ordered by `sequence` (creation
    order). In production this would be backed by a database table; here
    it's a static in-memory list seeded once at process start.
    """
    raw = [
        # (sequence, sku, category, quantity, status)
        (1, "ELEC-1001", "electronics", 12, "pending"),
        (2, "APRL-2001", "apparel", 30, "pending"),
        (3, "ELEC-1002", "electronics", 5, "fulfilled"),
        (4, "GROC-3001", "grocery", 100, "pending"),
        (5, "FURN-4001", "furniture", 2, "cancelled"),
        (6, "ELEC-1003", "electronics", 8, "pending"),
        (7, "APRL-2002", "apparel", 15, "fulfilled"),
        (8, "ELEC-1004", "electronics", 20, "cancelled"),
        (9, "GROC-3002", "grocery", 60, "fulfilled"),
        (10, "FURN-4002", "furniture", 4, "pending"),
        (11, "ELEC-1005", "electronics", 9, "pending"),
        (12, "APRL-2003", "apparel", 25, "cancelled"),
        (13, "GROC-3003", "grocery", 80, "pending"),
        (14, "ELEC-1006", "electronics", 6, "fulfilled"),
        (15, "FURN-4003", "furniture", 3, "fulfilled"),
        (16, "APRL-2004", "apparel", 18, "pending"),
        (17, "ELEC-1007", "electronics", 11, "pending"),
        (18, "GROC-3004", "grocery", 40, "cancelled"),
    ]
    return [
        Reservation(
            id=sequence,
            sku=sku,
            category=category,
            quantity=quantity,
            status=status,
            sequence=sequence,
        )
        for sequence, sku, category, quantity, status in raw
    ]


class ReservationRepository:
    """In-memory store of reservations, with cursor-based pagination over
    creation order (`sequence`), optionally scoped to a single category.
    """

    def __init__(self):
        self._reservations: list[Reservation] = _seed_reservations()

    def list_page(
        self,
        cursor: int | None,
        limit: int,
        category: str | None = None,
    ) -> list[Reservation]:
        """Return up to `limit` reservations ordered by `sequence`
        ascending, resuming after `cursor` (or from the beginning if
        `cursor` is None), optionally restricted to `category`.

        The category filter is applied *before* the cursor/limit slicing
        so that `next_cursor` (computed by the caller from the last
        returned item's `sequence`) always resumes correctly within the
        filtered set — an unrecognized category simply yields no matches
        rather than an error.
        """
        ordered = sorted(self._reservations, key=lambda r: r.sequence)
        if category is not None:
            ordered = [r for r in ordered if r.category == category]
        if cursor is not None:
            ordered = [r for r in ordered if r.sequence > cursor]
        return ordered[:limit]

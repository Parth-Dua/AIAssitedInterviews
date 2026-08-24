from app.domain.ticket import Ticket


class TicketRepository:
    """In-memory store of tickets, keyed by ticket id.

    In production this would be backed by a database table. `save` stores
    the exact `Ticket` object it's given, and `get` hands back that same
    object -- there's no serialization/deserialization step and no
    defensive copy in either direction. That's expected, intentional
    behavior for a lightweight in-memory store (it keeps things simple and
    fast), not a bug in this file.
    """

    def __init__(self):
        self._tickets: dict[int, Ticket] = {}

    def save(self, ticket: Ticket) -> None:
        self._tickets[ticket.id] = ticket

    def get(self, ticket_id: int) -> Ticket | None:
        return self._tickets.get(ticket_id)

    def list_all(self) -> list[Ticket]:
        return list(self._tickets.values())

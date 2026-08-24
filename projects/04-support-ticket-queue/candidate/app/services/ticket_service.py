from app.domain.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository


class TicketService:
    """Creates and manages support tickets.

    Business rules:
      1. Every new ticket starts in "open" status.
      2. If this service is configured with an auto-watch email (the
         support lead who should be CC'd on every new ticket, for
         example), that address is added to a ticket's watcher list
         automatically whenever the ticket is created.
      3. Any watchers explicitly supplied by the caller at creation time
         are preserved alongside the auto-watch email.
      4. Watchers can also be added to an existing ticket after creation.
    """

    def __init__(self, repository: TicketRepository, auto_watch_email: str | None = None):
        self._repository = repository
        self._auto_watch_email = auto_watch_email
        self._next_id = 1

    def create_ticket(self, subject: str, watchers: list[str] = []) -> Ticket:
        if self._auto_watch_email:
            watchers.append(self._auto_watch_email)
        ticket = Ticket(id=self._next_id, subject=subject, status="open", watchers=watchers)
        self._repository.save(ticket)
        self._next_id += 1
        return ticket

    def add_watcher(self, ticket_id: int, email: str) -> Ticket | None:
        ticket = self._repository.get(ticket_id)
        if ticket is None:
            return None
        ticket.watchers.append(email)
        return ticket

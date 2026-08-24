from app.repositories.ticket_repository import TicketRepository
from app.services.ticket_service import TicketService

AUTO_WATCH_EMAIL = "support-lead@company.example"


def make_service() -> TicketService:
    return TicketService(TicketRepository(), auto_watch_email=AUTO_WATCH_EMAIL)


def test_ticket_without_watchers_includes_auto_watch_email():
    service = make_service()
    ticket = service.create_ticket("Printer is on fire")
    assert AUTO_WATCH_EMAIL in ticket.watchers


def test_ticket_with_explicit_watchers_includes_both():
    service = make_service()
    ticket = service.create_ticket(
        "VPN keeps dropping", watchers=["alice@company.example"]
    )
    assert "alice@company.example" in ticket.watchers
    assert AUTO_WATCH_EMAIL in ticket.watchers


def test_adding_watcher_to_one_ticket_does_not_affect_another():
    """Bug report from support: 'Someone noticed that when they added a
    coworker as a watcher on one ticket, that same coworker mysteriously
    started showing up as a watcher on several other, completely unrelated
    tickets that were created around the same time.'
    """
    service = make_service()
    first = service.create_ticket("Printer is on fire")
    second = service.create_ticket("VPN keeps dropping")

    service.add_watcher(first.id, "bob@company.example")

    assert "bob@company.example" in first.watchers
    assert "bob@company.example" not in second.watchers, (
        "adding a watcher to one ticket must not add a watcher to a "
        "different, unrelated ticket"
    )


def test_successive_tickets_without_watchers_have_stable_watcher_count():
    """Bug report from support: 'Also, some newly created tickets already
    have 3-4 people watching them who were never explicitly added.'
    """
    service = make_service()
    tickets = [service.create_ticket(f"Ticket {i}") for i in range(4)]

    for ticket in tickets:
        assert len(ticket.watchers) == 1, (
            f"ticket {ticket.id!r} should only have the auto-watch email "
            f"as a watcher, got {ticket.watchers!r}"
        )

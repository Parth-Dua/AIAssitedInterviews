"""Hidden tests. Copy this file into candidate/tests/ (it is not present in
the candidate repo) and run `pytest` from candidate/ after applying a
candidate's fix, or after applying reference_solution/ticket_service.py to
validate the answer key.
"""

from app.repositories.ticket_repository import TicketRepository
from app.services.ticket_service import TicketService

AUTO_WATCH_EMAIL = "support-lead@company.example"


def make_service() -> TicketService:
    return TicketService(TicketRepository(), auto_watch_email=AUTO_WATCH_EMAIL)


def test_create_ticket_does_not_mutate_caller_supplied_watchers_list():
    """The service must not mutate a list object the caller still holds a
    reference to. Catches a fix that stops sharing a default across calls
    but still appends directly into whatever list object the caller passed
    in as `watchers`.
    """
    service = make_service()
    my_watchers = ["carol@company.example"]
    original_snapshot = list(my_watchers)

    service.create_ticket("Onboarding request", watchers=my_watchers)

    assert my_watchers == original_snapshot, (
        "the caller's own list object must not be modified by create_ticket"
    )


def test_tickets_without_watchers_get_independent_list_objects():
    """Even when neither ticket is given explicit watchers, each ticket
    must end up with its own list object -- not two references to the same
    underlying list.
    """
    service = make_service()
    first = service.create_ticket("Ticket A")
    second = service.create_ticket("Ticket B")
    assert first.watchers is not second.watchers


def test_interleaved_explicit_and_default_watchers_stay_isolated():
    service = make_service()
    a = service.create_ticket("A")  # no explicit watchers
    b = service.create_ticket("B", watchers=["dave@company.example"])
    c = service.create_ticket("C")  # no explicit watchers
    service.add_watcher(b.id, "eve@company.example")

    assert "eve@company.example" not in a.watchers
    assert "eve@company.example" not in c.watchers
    assert "dave@company.example" not in a.watchers
    assert "dave@company.example" not in c.watchers
    assert AUTO_WATCH_EMAIL in a.watchers
    assert AUTO_WATCH_EMAIL in c.watchers


def test_auto_watch_email_present_regardless_of_creation_path():
    service = make_service()
    no_explicit = service.create_ticket("No explicit watchers")
    with_explicit = service.create_ticket(
        "With explicit watchers", watchers=["frank@company.example"]
    )
    assert AUTO_WATCH_EMAIL in no_explicit.watchers
    assert AUTO_WATCH_EMAIL in with_explicit.watchers

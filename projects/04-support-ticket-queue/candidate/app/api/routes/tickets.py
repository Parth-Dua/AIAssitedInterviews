from fastapi import APIRouter, HTTPException

from app.models.schemas import AddWatcherRequest, CreateTicketRequest, TicketOut
from app.repositories.ticket_repository import TicketRepository
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])

_repository = TicketRepository()
_service = TicketService(_repository, auto_watch_email="support-lead@company.example")


def _to_out(ticket) -> TicketOut:
    return TicketOut(
        id=ticket.id,
        subject=ticket.subject,
        status=ticket.status,
        watchers=ticket.watchers,
    )


@router.post("", response_model=TicketOut)
def create_ticket(request: CreateTicketRequest) -> TicketOut:
    """Create a new support ticket. The support lead is auto-watched on
    every ticket; if the caller supplies explicit watchers, they're added
    on top of that.
    """
    if request.watchers:
        ticket = _service.create_ticket(request.subject, request.watchers)
    else:
        ticket = _service.create_ticket(request.subject)
    return _to_out(ticket)


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int) -> TicketOut:
    ticket = _repository.get(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="ticket not found")
    return _to_out(ticket)


@router.post("/{ticket_id}/watchers", response_model=TicketOut)
def add_watcher(ticket_id: int, request: AddWatcherRequest) -> TicketOut:
    ticket = _service.add_watcher(ticket_id, request.email)
    if ticket is None:
        raise HTTPException(status_code=404, detail="ticket not found")
    return _to_out(ticket)

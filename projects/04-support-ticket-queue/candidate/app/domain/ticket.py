from dataclasses import dataclass


@dataclass
class Ticket:
    """A support ticket.

    This is a plain domain object, not a Pydantic model. The Pydantic
    models in app/models/schemas.py describe the request/response wire
    format; this describes the business entity itself, independent of how
    it's serialized over HTTP.
    """

    id: int
    subject: str
    status: str
    watchers: list[str]

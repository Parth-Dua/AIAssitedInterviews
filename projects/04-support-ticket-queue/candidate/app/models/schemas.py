from typing import List

from pydantic import BaseModel


class CreateTicketRequest(BaseModel):
    subject: str
    watchers: List[str] = []


class AddWatcherRequest(BaseModel):
    email: str


class TicketOut(BaseModel):
    id: int
    subject: str
    status: str
    watchers: List[str]

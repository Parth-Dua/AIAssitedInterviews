from datetime import date

from pydantic import BaseModel, ConfigDict


class LoanOut(BaseModel):
    """API representation of a loan record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    book_title: str
    patron_name: str
    checked_out_at: date
    due_at: date
    renewed_due_at: date | None
    returned_at: date | None

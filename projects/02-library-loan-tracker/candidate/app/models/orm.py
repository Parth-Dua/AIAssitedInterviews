from datetime import date

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Loan(Base):
    """A single book checked out to a patron."""

    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    book_title: Mapped[str] = mapped_column(String(255), nullable=False)
    patron_name: Mapped[str] = mapped_column(String(255), nullable=False)
    checked_out_at: Mapped[date] = mapped_column(Date, nullable=False)
    due_at: Mapped[date] = mapped_column(Date, nullable=False)

    # Set by a librarian when a patron renews a loan; when present this is
    # the loan's *current* due date and supersedes due_at.
    renewed_due_at: Mapped[date | None] = mapped_column(Date, nullable=True, default=None)

    # Set when the book is checked back in. A loan with a non-null
    # returned_at is never overdue, regardless of due date.
    returned_at: Mapped[date | None] = mapped_column(Date, nullable=True, default=None)

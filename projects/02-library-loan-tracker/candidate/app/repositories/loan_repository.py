from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.orm import Loan


class LoanRepository:
    """Data-access layer for Loan rows."""

    def get_overdue_loans(self, session: Session, as_of: date) -> list[Loan]:
        """Return loans that are not yet returned and are overdue as of
        `as_of`.

        A loan's *effective* due date is its renewed_due_at when the loan
        has been renewed, otherwise its original due_at.
        """
        stmt = select(Loan).where(
            Loan.returned_at.is_(None),
            Loan.due_at < as_of,
        )
        return list(session.execute(stmt).scalars().all())

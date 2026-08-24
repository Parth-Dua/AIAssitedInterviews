from datetime import date

from sqlalchemy.orm import Session

from app.models.orm import Loan
from app.repositories.loan_repository import LoanRepository


class LoanService:
    """Thin orchestration layer over LoanRepository.

    Business rules (see the library ops wiki in the real system, summarized
    here since that wiki isn't included in this exercise):
      1. A loan is overdue when it has not been returned and its effective
         due date (the renewed due date if the loan was renewed, otherwise
         the original due date) is strictly before the reference date.
      2. "Reference date" (`as_of`) is always supplied by the caller rather
         than read from the system clock, so overdue reports are
         reproducible for a given day.
    """

    def __init__(self, repository: LoanRepository | None = None):
        self._repository = repository or LoanRepository()

    def list_overdue(self, session: Session, as_of: date) -> list[Loan]:
        return self._repository.get_overdue_loans(session, as_of)

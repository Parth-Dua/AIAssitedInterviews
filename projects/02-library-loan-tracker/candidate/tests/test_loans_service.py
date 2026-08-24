from datetime import date

from app.models.orm import Loan
from app.repositories.loan_repository import LoanRepository
from app.services.loan_service import LoanService


def make_service() -> LoanService:
    return LoanService(LoanRepository())


def add_loan(session, **kwargs) -> Loan:
    loan = Loan(**kwargs)
    session.add(loan)
    session.commit()
    session.refresh(loan)
    return loan


def test_never_renewed_past_due_loan_is_overdue(db_session):
    add_loan(
        db_session,
        book_title="Dune",
        patron_name="Alex Chen",
        checked_out_at=date(2026, 7, 1),
        due_at=date(2026, 7, 15),
    )
    service = make_service()

    overdue = service.list_overdue(db_session, as_of=date(2026, 7, 20))

    assert len(overdue) == 1
    assert overdue[0].book_title == "Dune"


def test_loan_due_in_the_future_is_not_overdue(db_session):
    add_loan(
        db_session,
        book_title="Foundation",
        patron_name="Sam Iyer",
        checked_out_at=date(2026, 7, 1),
        due_at=date(2026, 8, 1),
    )
    service = make_service()

    overdue = service.list_overdue(db_session, as_of=date(2026, 7, 20))

    assert overdue == []


def test_returned_loan_is_never_overdue(db_session):
    add_loan(
        db_session,
        book_title="Neuromancer",
        patron_name="Jordan Blake",
        checked_out_at=date(2026, 6, 1),
        due_at=date(2026, 6, 15),
        returned_at=date(2026, 6, 10),
    )
    service = make_service()

    overdue = service.list_overdue(db_session, as_of=date(2026, 7, 20))

    assert overdue == []


def test_renewed_loan_with_future_renewed_due_date_is_not_overdue(db_session):
    """Bug report from a librarian: 'A patron renewed their loan last week,
    which should have pushed the due date out two weeks. The book is still
    showing up in the librarian's overdue list using the original due date,
    even though the renewal was recorded in the system.'

    Once a loan is renewed, overdue status must be evaluated against the
    renewed due date, not the original one.
    """
    add_loan(
        db_session,
        book_title="Snow Crash",
        patron_name="Riley Nakamura",
        checked_out_at=date(2026, 6, 1),
        due_at=date(2026, 6, 15),
        renewed_due_at=date(2026, 8, 1),
    )
    service = make_service()

    overdue = service.list_overdue(db_session, as_of=date(2026, 7, 20))

    assert overdue == [], (
        "the loan was renewed to a due date in the future (2026-08-01); it "
        "should not appear as overdue even though its original due_at "
        "(2026-06-15) has already passed"
    )

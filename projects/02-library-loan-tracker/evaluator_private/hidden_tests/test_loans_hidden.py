"""Hidden tests. Copy this file into candidate/tests/ (it is not present in
the candidate repo) and run `pytest` from candidate/ after applying a
candidate's fix, or after applying
reference_solution/loan_repository.py to validate the answer key.

Relies on the `db_session` fixture already defined in candidate/tests/conftest.py.
"""

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


def test_overdue_boundary_is_strictly_before_as_of(db_session):
    """A loan due exactly on as_of is not yet overdue (due_at < as_of, not
    <=)."""
    add_loan(
        db_session,
        book_title="The Hobbit",
        patron_name="Casey Ito",
        checked_out_at=date(2026, 7, 1),
        due_at=date(2026, 7, 20),
    )
    service = make_service()

    overdue = service.list_overdue(db_session, as_of=date(2026, 7, 20))

    assert overdue == []


def test_overdue_boundary_one_day_past_as_of(db_session):
    add_loan(
        db_session,
        book_title="The Hobbit",
        patron_name="Casey Ito",
        checked_out_at=date(2026, 7, 1),
        due_at=date(2026, 7, 19),
    )
    service = make_service()

    overdue = service.list_overdue(db_session, as_of=date(2026, 7, 20))

    assert len(overdue) == 1


def test_renewed_loan_still_overdue_if_renewed_due_date_also_past(db_session):
    """A loan can be renewed and still be overdue: the renewal date itself
    must be checked against as_of, not just "renewed means not overdue"."""
    add_loan(
        db_session,
        book_title="1984",
        patron_name="Morgan Diallo",
        checked_out_at=date(2026, 6, 1),
        due_at=date(2026, 6, 15),
        renewed_due_at=date(2026, 7, 10),
    )
    service = make_service()

    overdue = service.list_overdue(db_session, as_of=date(2026, 7, 20))

    assert len(overdue) == 1
    assert overdue[0].book_title == "1984"


def test_shortened_loan_renewed_due_date_earlier_than_original_due_at(db_session):
    """A librarian can also shorten a loan: renewed_due_at earlier than the
    original due_at. This loan's original due_at is still in the future,
    but its effective (renewed) due date has already passed, so it must
    show up as overdue.

    This specifically catches a fix that filters `Loan.due_at < as_of` in
    SQL and only checks renewed_due_at afterward (e.g. in Python): such a
    fix never even fetches this row as a candidate, because its original
    due_at (2026-08-01) is not before as_of, even though its effective due
    date (2026-07-10) is.
    """
    add_loan(
        db_session,
        book_title="Brave New World",
        patron_name="Priya Patel",
        checked_out_at=date(2026, 6, 1),
        due_at=date(2026, 8, 1),
        renewed_due_at=date(2026, 7, 10),
    )
    service = make_service()

    overdue = service.list_overdue(db_session, as_of=date(2026, 7, 20))

    assert len(overdue) == 1
    assert overdue[0].book_title == "Brave New World"


def test_returned_loan_excluded_even_if_effective_due_date_in_past(db_session):
    """Invariant: a returned loan is never overdue, even when both its
    original and renewed due dates are in the past."""
    add_loan(
        db_session,
        book_title="Dune",
        patron_name="Alex Chen",
        checked_out_at=date(2026, 5, 1),
        due_at=date(2026, 5, 15),
        renewed_due_at=date(2026, 6, 1),
        returned_at=date(2026, 5, 28),
    )
    service = make_service()

    overdue = service.list_overdue(db_session, as_of=date(2026, 7, 20))

    assert overdue == []


def test_multiple_loans_mixed_states_returns_only_the_overdue_ones(db_session):
    add_loan(
        db_session,
        book_title="Overdue, never renewed",
        patron_name="A",
        checked_out_at=date(2026, 6, 1),
        due_at=date(2026, 7, 1),
    )
    add_loan(
        db_session,
        book_title="Not due yet",
        patron_name="B",
        checked_out_at=date(2026, 7, 1),
        due_at=date(2026, 8, 1),
    )
    add_loan(
        db_session,
        book_title="Returned late",
        patron_name="C",
        checked_out_at=date(2026, 6, 1),
        due_at=date(2026, 6, 10),
        returned_at=date(2026, 6, 20),
    )
    add_loan(
        db_session,
        book_title="Renewed into the future",
        patron_name="D",
        checked_out_at=date(2026, 6, 1),
        due_at=date(2026, 6, 15),
        renewed_due_at=date(2026, 8, 1),
    )
    add_loan(
        db_session,
        book_title="Renewed but still overdue",
        patron_name="E",
        checked_out_at=date(2026, 6, 1),
        due_at=date(2026, 6, 15),
        renewed_due_at=date(2026, 7, 5),
    )
    service = make_service()

    overdue = service.list_overdue(db_session, as_of=date(2026, 7, 20))
    titles = {loan.book_title for loan in overdue}

    assert titles == {"Overdue, never renewed", "Renewed but still overdue"}

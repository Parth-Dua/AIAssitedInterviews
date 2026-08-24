from datetime import date

from app.models.orm import Loan


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_overdue_endpoint_returns_past_due_loan(client, db_session):
    loan = Loan(
        book_title="Dune",
        patron_name="Alex Chen",
        checked_out_at=date(2026, 7, 1),
        due_at=date(2026, 7, 15),
    )
    db_session.add(loan)
    db_session.commit()

    response = client.get("/loans/overdue", params={"as_of": "2026-07-20"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["book_title"] == "Dune"


def test_overdue_endpoint_requires_as_of(client):
    response = client.get("/loans/overdue")
    assert response.status_code == 422

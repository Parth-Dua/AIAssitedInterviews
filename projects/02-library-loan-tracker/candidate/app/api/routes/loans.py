from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models.schemas import LoanOut
from app.services.loan_service import LoanService

router = APIRouter(prefix="/loans", tags=["loans"])

_service = LoanService()


@router.get("/overdue", response_model=list[LoanOut])
def get_overdue_loans(
    as_of: date, session: Session = Depends(get_session)
) -> list[LoanOut]:
    """Return loans that are overdue as of `as_of`. Used by the librarian
    dashboard to build the daily overdue-notice list.
    """
    loans = _service.list_overdue(session, as_of)
    return [LoanOut.model_validate(loan) for loan in loans]

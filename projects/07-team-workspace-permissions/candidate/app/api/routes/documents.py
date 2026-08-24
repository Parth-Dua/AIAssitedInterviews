from fastapi import APIRouter, Header, HTTPException

from app.api.deps import document_service
from app.models.schemas import Document, DocumentPatchRequest
from app.services.document_service import DocumentNotFoundError, PermissionDeniedError

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/{document_id}", response_model=Document)
def get_document(
    document_id: int, x_user_id: int = Header(..., alias="X-User-Id")
) -> Document:
    """Return a document. The caller must be a member of the document's
    workspace (any role).
    """
    try:
        return document_service.get_document(x_user_id, document_id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="document not found")
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc))


@router.patch("/{document_id}", response_model=Document)
def update_document(
    document_id: int,
    patch: DocumentPatchRequest,
    x_user_id: int = Header(..., alias="X-User-Id"),
) -> Document:
    """Partially update a document's title and/or content."""
    try:
        return document_service.update_document(x_user_id, document_id, patch)
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="document not found")
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc))


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int, x_user_id: int = Header(..., alias="X-User-Id")
) -> None:
    """Delete a document."""
    try:
        document_service.delete_document(x_user_id, document_id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="document not found")
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

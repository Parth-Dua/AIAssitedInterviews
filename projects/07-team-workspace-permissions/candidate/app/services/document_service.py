from app.models.schemas import Document, DocumentPatchRequest
from app.repositories.document_repository import DocumentRepository
from app.services.permission_service import PermissionService


class DocumentNotFoundError(Exception):
    pass


class PermissionDeniedError(Exception):
    pass


class DocumentService:
    """Read/write orchestration for documents. Every access is gated
    through PermissionService — this class never makes an authorization
    decision itself.
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        permission_service: PermissionService,
    ):
        self._document_repository = document_repository
        self._permission_service = permission_service

    def get_document(self, user_id: int, document_id: int) -> Document:
        document = self._require_document(document_id)
        if not self._permission_service.can_read_document(user_id, document):
            raise PermissionDeniedError("not a member of this document's workspace")
        return document

    def update_document(
        self, user_id: int, document_id: int, patch: DocumentPatchRequest
    ) -> Document:
        document = self._require_document(document_id)
        if not self._permission_service.can_edit_document(user_id, document):
            raise PermissionDeniedError("not permitted to edit this document")
        updated = self._document_repository.update_document(
            document_id, title=patch.title, content=patch.content
        )
        assert updated is not None  # document existence already checked above
        return updated

    def delete_document(self, user_id: int, document_id: int) -> None:
        document = self._require_document(document_id)
        if not self._permission_service.can_manage_document(user_id, document):
            raise PermissionDeniedError("not permitted to delete this document")
        self._document_repository.delete_document(document_id)

    def _require_document(self, document_id: int) -> Document:
        document = self._document_repository.get_document(document_id)
        if document is None:
            raise DocumentNotFoundError(f"document {document_id} not found")
        return document

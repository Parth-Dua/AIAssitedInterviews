from app.models.schemas import Document


class DocumentRepository:
    """In-memory store of documents. In production this would be a table
    keyed by document id, partitioned by workspace_id.
    """

    def __init__(self):
        self._documents: dict[int, Document] = {
            1: Document(
                id=1,
                workspace_id="marketing",
                owner_id=3,
                title="Q3 Campaign Brief",
                content="Draft messaging for the Q3 product launch.",
            ),
            2: Document(
                id=2,
                workspace_id="marketing",
                owner_id=1,
                title="Marketing OKRs",
                content="Q3 objectives and key results for the marketing team.",
            ),
            3: Document(
                id=3,
                workspace_id="marketing",
                owner_id=2,
                title="Brand Guidelines",
                content="Logo usage, color palette, and tone of voice.",
            ),
            4: Document(
                id=4,
                workspace_id="engineering",
                owner_id=2,
                title="Deploy Runbook",
                content="Steps for a production deployment and rollback.",
            ),
            5: Document(
                id=5,
                workspace_id="engineering",
                owner_id=3,
                title="Incident Postmortem Template",
                content="Standard template for writing up an incident postmortem.",
            ),
        }

    def get_document(self, document_id: int) -> Document | None:
        return self._documents.get(document_id)

    def update_document(
        self,
        document_id: int,
        *,
        title: str | None = None,
        content: str | None = None,
    ) -> Document | None:
        document = self._documents.get(document_id)
        if document is None:
            return None
        updated = document.model_copy(
            update={
                "title": title if title is not None else document.title,
                "content": content if content is not None else document.content,
            }
        )
        self._documents[document_id] = updated
        return updated

    def delete_document(self, document_id: int) -> bool:
        if document_id in self._documents:
            del self._documents[document_id]
            return True
        return False

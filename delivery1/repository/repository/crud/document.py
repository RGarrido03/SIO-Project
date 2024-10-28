from repository.crud.base import CRUDBase
from repository.models.document import Document, DocumentCreate


class CRUDDocument(CRUDBase[Document, DocumentCreate]):
    def __init__(self) -> None:
        super().__init__(Document)


crud_document = CRUDDocument()

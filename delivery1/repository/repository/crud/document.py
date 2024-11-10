import os
import uuid
from datetime import datetime
from hashlib import sha256
from typing import Literal

from fastapi import UploadFile
from sqlalchemy.sql.operators import ge, le, eq
from sqlmodel import select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from repository.config.database import get_session
from repository.crud.base import CRUDBase
from repository.models.document import Document, DocumentCreate
from repository.models.permission import RoleEnum, DocumentPermission


class CRUDDocument(CRUDBase[Document, DocumentCreate, uuid.UUID]):
    def __init__(self) -> None:
        super().__init__(Document)

    async def add_new(self, document: DocumentCreate, file: UploadFile) -> Document:

        if (sha256(await file.read()).hexdigest()) != document.file_handle:

            raise ValueError("File handle does not match the file content")

        path = f"static/{document.organization_name}"
        os.makedirs(path, exist_ok=True)
        with open(f"{path}/{document.file_handle}", "wb") as f:
            f.write(await file.read())

        return await self.create(document)

    async def get_by_name(self, name: str) -> Document | None:
        async with get_session() as session:
            result = await session.exec(select(Document).where(Document.name == name))
            return result.first()

    async def get_all(
        self,
        username: str | None = None,
        date: datetime | None = None,
        date_order: Literal["nt", "ot", "et"] = "nt",
    ) -> list[Document]:
        async with get_session() as session:
            query: SelectOfScalar[Document] = select(Document)

            if username:
                query = query.where(Document.creator_username == username)

            if date:
                operators = {
                    "nt": ge,
                    "ot": le,
                    "et": eq,
                }
                query = query.where(operators[date_order](Document.create_date, date))

            result = await session.exec(query)
            return list(result.all())

    async def add_acl(
        self, document: Document, role: RoleEnum, permission: DocumentPermission
    ) -> Document:
        if role not in document.acl:
            document.acl[role] = set()
        document.acl[role].add(permission)
        return await self._add_to_db(document)

    async def remove_acl(
        self, document: Document, role: RoleEnum, permission: DocumentPermission
    ) -> Document:
        if role not in document.acl:
            return document
        document.acl[role].discard(permission)
        return await self._add_to_db(document)

    async def delete(self, document_handle: uuid.UUID) -> bool:
        document = await self.get(document_handle)
        if document is None:
            return False

        document.file_handle = None
        await self._add_to_db(document)
        return True


crud_document = CRUDDocument()

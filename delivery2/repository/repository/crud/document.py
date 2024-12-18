import base64
import os
import uuid
from datetime import datetime
from hashlib import sha256
from typing import Literal

from sqlalchemy import func, literal_column, Grouping
from sqlalchemy.sql.operators import ge, le, eq
from sqlmodel import select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from repository.config.database import get_session
from repository.crud.base import CRUDBase
from repository.models.document import (
    Document,
    DocumentCreate,
    DocumentRolesByPermission,
)
from repository.models.permission import DocumentPermission


class CRUDDocument(CRUDBase[Document, DocumentCreate, uuid.UUID]):
    def __init__(self) -> None:
        super().__init__(Document)

    async def add_new(self, document: DocumentCreate, file: str) -> Document:
        file_content = base64.decodebytes(file.encode())
        if (sha256(file.encode()).hexdigest()) != document.file_handle:
            raise ValueError("File handle does not match the file content")

        if await self.get_by_name_and_organization(
            document.name, document.organization_name
        ):
            raise ValueError("Document with this name already exists")

        path = f"static/docs"
        os.makedirs(path, exist_ok=True)
        with open(f"{path}/{document.file_handle}", "wb") as f:
            f.write(file_content)

        return await self.create(document)

    async def get_by_name_and_organization(
        self, name: str, organization_name: str
    ) -> Document | None:
        async with get_session() as session:
            result = await session.exec(
                select(Document)
                .where(Document.name == name)
                .where(Document.organization_name == organization_name)
            )

            return result.first()

    async def get_all(
        self,
        username: str | None = None,
        date: datetime | None = None,
        date_order: Literal["nt", "ot", "et"] = "nt",
        organization_name: str | None = None,
    ) -> list[Document]:
        async with get_session() as session:
            query: SelectOfScalar[Document] = select(Document)

            if username:
                query = query.where(Document.creator_username == username)

            if organization_name:
                query = query.where(Document.organization_name == organization_name)

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
        self, document: Document, role: str, permission: DocumentPermission
    ) -> Document:
        if role not in document.acl:
            document.acl[role] = set()
        document.acl[role].add(permission)
        return await self._add_to_db(document)

    async def remove_acl(
        self, document: Document, role: str, permission: DocumentPermission
    ) -> Document:
        if role not in document.acl:
            return document
        if (
            permission == DocumentPermission.DOC_ACL
            and sum(1 for roles in document.acl.values() if permission in roles) == 1
        ):
            raise ValueError("Cannot remove the last ACL permission from a role")
        document.acl[role].discard(permission)
        return await self._add_to_db(document)

    async def delete(self, document_handle: uuid.UUID, username: str) -> bool:
        document = await self.get(document_handle)
        if document is None:
            return False

        document.file_handle = None
        document.deleter_username = username
        await self._add_to_db(document)
        return True

    async def get_roles_by_permission(
        self, organization_name: str, permission: DocumentPermission
    ) -> list[DocumentRolesByPermission]:
        async with get_session() as session:
            jsonb_each = func.jsonb_each(Document.acl)

            each_key = Grouping(
                Grouping(jsonb_each).op(".")(literal_column("key"))
            ).label("role")
            each_value = Grouping(jsonb_each).op(".")(literal_column("value"))
            value_set = Grouping(func.jsonb_array_elements_text(each_value)).label(
                "permission"
            )

            subquery = (
                select(Document.name.label("name"), each_key, value_set)  # type: ignore
                .select_from(Document)
                .where(Document.organization_name == organization_name)
            )

            query = (
                select(
                    subquery.c.name,
                    func.array_agg(subquery.c.role).label("roles_with_permission"),
                )
                .select_from(subquery)
                .where(subquery.c.permission == permission)
                .group_by(subquery.c.name)
            )

            result = await session.exec(query)
            result_list: list[tuple[str, list[str]]] = list(result.all())
            return [
                DocumentRolesByPermission(name=name, roles=roles)
                for name, roles in result_list
            ]


crud_document = CRUDDocument()

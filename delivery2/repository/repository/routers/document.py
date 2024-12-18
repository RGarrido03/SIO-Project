import base64
import pathlib
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, HTTPException, Security

from repository.crud.document import crud_document
from repository.models.document import (
    Document,
    DocumentCreate,
    DocumentBase,
    DocumentCreateWithFile,
)
from repository.models.permission import DocumentPermission, Permission
from repository.models.relations import SubjectOrganizationLink
from repository.utils.auth.authorization_handler import (
    get_current_user,
    check_permission,
    check_doc_permission,
)

router = APIRouter(prefix="/document", tags=["Document"])


@router.post("", description="rep_add_doc")
async def create_document(
    doc: DocumentCreateWithFile,
    link: SubjectOrganizationLink = Security(
        check_permission, scopes=[Permission.DOC_NEW]
    ),
) -> Document:
    try:
        doc.creator_username = link.subject_username
        doc.organization_name = link.organization_name
        doc.acl = {role: {DocumentPermission.DOC_ACL} for role in link.role_ids}

        return await crud_document.add_new(
            DocumentCreate.model_validate(doc), doc.file_content
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{name}", description="rep_get_doc_metadata")
async def get_document_metadata(
    name: str,
    link: SubjectOrganizationLink = Security(get_current_user),
) -> Document:
    doc = await crud_document.get_by_name_and_organization(name, link.organization_name)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    check_doc_permission(DocumentPermission.DOC_READ, doc.acl, link.role_ids)
    return doc


@router.get("/handle/{handle}", description="rep_get_file")
async def get_document_by_handle(
    handle: str,
) -> str:
    path = pathlib.Path(f"static/docs/{handle}")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    with open(f"static/docs/{handle}", "rb") as f:
        file_content = f.read()

    return base64.encodebytes(file_content).decode()


@router.get("", response_model=list[DocumentBase], description="rep_list_docs")
async def list_documents(
    username: str | None = None,
    date: datetime | None = None,
    date_order: Literal["nt", "ot", "et"] = "nt",
    link: SubjectOrganizationLink = Security(get_current_user),
) -> list[Document]:
    return await crud_document.get_all(
        username, date, date_order, link.organization_name
    )


@router.patch("/{name}/acl", description="rep_acl_doc")
async def update_document_acl(
    name: str,
    role: str,
    add: bool,
    permission: DocumentPermission,
    link: SubjectOrganizationLink = Security(get_current_user),
) -> Document:
    doc = await crud_document.get_by_name_and_organization(name, link.organization_name)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    check_doc_permission(DocumentPermission.DOC_ACL, doc.acl, link.role_ids)
    try:
        if add:
            return await crud_document.add_acl(doc, role, permission)
        return await crud_document.remove_acl(doc, role, permission)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{name}", description="rep_delete_doc")
async def delete_document(
    name: str,
    link: SubjectOrganizationLink = Security(get_current_user),
) -> str:
    doc = await crud_document.get_by_name_and_organization(name, link.organization_name)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    check_doc_permission(DocumentPermission.DOC_DELETE, doc.acl, link.role_ids)
    await crud_document.delete(doc.document_handle, link.subject.username)
    return doc.file_handle or ""

import json
import os
from datetime import datetime
from typing import Literal, Annotated

from fastapi import APIRouter, UploadFile, HTTPException, Form, File, Security

from repository.crud.document import crud_document
from repository.models import SubjectOrganizationLink
from repository.models.document import Document, DocumentCreate, DocumentBase, DocumentCreateWithFile
from repository.models.permission import RoleEnum, DocumentPermission
from repository.utils.auth.authorization_handler import get_current_user
from repository.utils.encryption.encryptors import encrypt_symmetric

router = APIRouter(prefix="/document", tags=["Document"])


@router.post("")
async def create_document(
        doc: DocumentCreateWithFile,
    link: SubjectOrganizationLink = Security(get_current_user),
) -> Document:
    try:
        # TODO FIXME NEXT DEILVERY
        # acl_dict = json.loads(acl)
        # formatted_acl = {
        #     RoleEnum(role): (
        #         {DocumentPermission(perm)}
        #         if isinstance(perm, str)
        #         else {DocumentPermission(p) for p in perm}
        #     )
        #     for role, perm in acl_dict.items()
        # }

        doc.creator_username = link.subject_username
        doc.organization_name = link.organization_name

        return await crud_document.add_new(DocumentCreate.model_validate(doc), doc.file_content)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{name}", response_model=DocumentBase)
async def get_document_metadata(
    name: str,
    _: SubjectOrganizationLink = Security(get_current_user),
) -> Document:
    doc = await crud_document.get_by_name(name)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("", response_model=list[DocumentBase])
async def list_documents(
    username: str | None = None,
    date: datetime | None = None,
    date_order: Literal["nt", "ot", "et"] = "nt",
    _: SubjectOrganizationLink = Security(get_current_user),
) -> list[Document]:
    return await crud_document.get_all(username, date, date_order)


@router.patch("/{name}/acl/add")
async def update_document_acl(
    name: str,
    role: RoleEnum,
    permission: DocumentPermission,
    _: SubjectOrganizationLink = Security(get_current_user),
) -> Document:
    doc = await crud_document.get_by_name(name)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return await crud_document.add_acl(doc, role, permission)


@router.patch("/{name}/acl/remove")
async def remove_document_acl(
    name: str,
    role: RoleEnum,
    permission: DocumentPermission,
    _: SubjectOrganizationLink = Security(get_current_user),
) -> Document:
    doc = await crud_document.get_by_name(name)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return await crud_document.remove_acl(doc, role, permission)


@router.delete("/{name}")
async def delete_document(
    name: str,
    link: SubjectOrganizationLink = Security(get_current_user),
) -> str:
    doc = await crud_document.get_by_name(name)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    await crud_document.delete(doc.document_handle, link.subject.username)
    # TODO: Set deleter username
    return doc.file_handle or ""

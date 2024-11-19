import json
from datetime import datetime
from typing import Literal, Annotated

from fastapi import APIRouter, UploadFile, HTTPException, Form, File, Security

from repository.crud.document import crud_document
from repository.models import SubjectOrganizationLink
from repository.models.document import Document, DocumentCreate, DocumentBase
from repository.models.permission import RoleEnum, DocumentPermission
from repository.utils.auth.authorization_handler import get_current_user

router = APIRouter(prefix="/document", tags=["Document"])


@router.post("")
async def create_document(
    name: Annotated[str, Form(...)],
    file_handle: Annotated[str, Form(...)],
    organization_name: Annotated[str, Form(...)],
    creator_username: Annotated[str, Form(...)],
    alg: Annotated[str, Form(...)],
    key: Annotated[str, Form(...)],
    iv: Annotated[str, Form(...)],
    acl: Annotated[dict | str, Form(media_type="application/json")],
    file: Annotated[UploadFile, File(...)],
    deleter_username: Annotated[str | None, Form(...)] = None,
    _: SubjectOrganizationLink = Security(get_current_user),
) -> Document:
    try:
        acl_dict = json.loads(acl)
        formatted_acl = {
            RoleEnum(role): (
                {DocumentPermission(perm)}
                if isinstance(perm, str)
                else {DocumentPermission(p) for p in perm}
            )
            for role, perm in acl_dict.items()
        }
        doc = DocumentCreate(
            name=name,
            file_handle=file_handle,
            organization_name=organization_name,
            creator_username=creator_username,
            deleter_username=deleter_username,
            alg=alg,
            iv=iv,
            key=key,
            acl=formatted_acl,
        )
        return await crud_document.add_new(doc, file)

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

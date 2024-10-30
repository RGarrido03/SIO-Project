from datetime import datetime
from typing import Literal

from fastapi import APIRouter, UploadFile, HTTPException

from repository.crud.document import crud_document
from repository.models.document import Document, DocumentCreate, DocumentBase
from repository.models.permission import RoleEnum, DocumentPermission

router = APIRouter(prefix="/document", tags=["Document"])


@router.post("")
async def create_document(document: DocumentCreate, file: UploadFile) -> Document:
    try:
        return await crud_document.add_new(document, file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{name}", response_model=DocumentBase)
async def get_document_metadata(name: str) -> Document:
    doc = await crud_document.get_by_name(name)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("", response_model=list[DocumentBase])
async def list_documents(
    username: str | None = None,
    date: datetime | None = None,
    date_order: Literal["nt", "ot", "et"] = "nt",
) -> list[Document]:
    return await crud_document.get_all(username, date, date_order)


@router.patch("/{name}/acl/add")
async def update_document_acl(
    name: str, role: RoleEnum, permission: DocumentPermission
) -> Document:
    doc = await crud_document.get_by_name(name)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return await crud_document.add_acl(doc, role, permission)


@router.patch("/{name}/acl/remove")
async def remove_document_acl(
    name: str, role: RoleEnum, permission: DocumentPermission
) -> Document:
    doc = await crud_document.get_by_name(name)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return await crud_document.remove_acl(doc, role, permission)


@router.delete("/{name}")
async def delete_document(name: str) -> str:
    doc = await crud_document.get_by_name(name)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    await crud_document.delete(doc.document_handle)
    return doc.file_handle or ""

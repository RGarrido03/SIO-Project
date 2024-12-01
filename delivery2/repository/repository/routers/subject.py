from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Security
from starlette.requests import Request

from repository.crud.organization import crud_organization
from repository.crud.subject import crud_subject
from repository.crud.subject_organization_link import crud_subject_organization_link
from repository.models.permission import RoleEnum
from repository.models.relations import SubjectOrganizationLink
from repository.models.session import Session, SessionCreate
from repository.models.subject import SubjectCreate, Subject, SubjectActiveListing
from repository.utils.auth.authorization_handler import get_current_user

router = APIRouter(prefix="/subject", tags=["Subject"])


@router.post("")
async def create_subject(
    subject: SubjectCreate,
    link: SubjectOrganizationLink = Security(get_current_user),
) -> Subject:
    try:
        obj = await crud_subject.create(subject)
        await crud_organization.add_subject(
            link.organization_name, subject.username, obj.public_key.id
        )
        return obj.subject
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/session")
async def create_session(info: SessionCreate, request: Request) -> str:
    try:
        token, public_key = await crud_subject_organization_link.create_session(info)
        request.state.public_key = public_key
        return token
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/session/role")
async def add_role(
    role: RoleEnum, link: Annotated[SubjectOrganizationLink, Depends(get_current_user)]
) -> str:
    try:
        return await crud_subject_organization_link.add_role_to_session(link, role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def get_subjects_by_organization(
    link: Annotated[SubjectOrganizationLink, Depends(get_current_user)],
    username: str | None = None,
) -> list[SubjectActiveListing]:
    try:
        return await crud_subject_organization_link.get_subjects_by_organization(
            link.organization_name, username
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/session/role")
async def drop_role(
    role: RoleEnum, link: Annotated[SubjectOrganizationLink, Depends(get_current_user)]
) -> str:
    try:
        return await crud_subject_organization_link.drop_role_from_session(link, role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/activation")
async def set_activation(
    username: str,
    active: bool,
    _: Annotated[SubjectOrganizationLink, Depends(get_current_user)],
) -> Subject:
    result = await crud_subject.set_active(username, active)
    if result is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return result

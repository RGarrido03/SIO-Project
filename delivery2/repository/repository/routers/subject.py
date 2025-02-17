from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Security
from starlette.requests import Request

from repository.crud.subject import crud_subject
from repository.crud.subject_organization_link import crud_subject_organization_link
from repository.models.permission import Permission
from repository.models.relations import (
    SubjectOrganizationLink,
    SubjectOrganizationLinkCreate,
)
from repository.models.session import SessionCreate
from repository.models.subject import SubjectCreate, Subject, SubjectActiveListing
from repository.utils.auth.authorization_handler import (
    get_current_user,
    check_permission,
)

router = APIRouter(prefix="/subject", tags=["Subject"])


@router.post("", description="rep_add_subject")
async def create_subject(
    subject: SubjectCreate,
    link: SubjectOrganizationLink = Security(
        check_permission, scopes=[Permission.SUBJECT_NEW]
    ),
) -> Subject:
    obj = await crud_subject.create(subject)
    await crud_subject_organization_link.create(
        SubjectOrganizationLinkCreate(
            organization_name=link.organization_name,
            subject_username=obj.subject.username,
            public_key_id=obj.public_key.id,
        )
    )
    return obj.subject


@router.post("/role", description="rep_add_permission")
async def add_role_to_subject(
    role: str,
    username: str,
    link: Annotated[
        SubjectOrganizationLink,
        Security(check_permission, scopes=[Permission.ROLE_MOD]),
    ],
) -> set[str]:
    new_link = await crud_subject_organization_link.manage_subject_role(
        link.organization_name, username, role, "add"
    )
    return new_link.role_ids


@router.post("/session", description="rep_create_session")
async def create_session(info: SessionCreate, request: Request) -> str:
    token, public_key = await crud_subject_organization_link.create_session(info)
    request.state.public_key = public_key
    return token


@router.post("/session/role", description="rep_assume_role")
async def add_role(
    role: str, link: Annotated[SubjectOrganizationLink, Depends(get_current_user)]
) -> str:
    return await crud_subject_organization_link.add_role_to_session(link, role)


@router.get("/session/role", description="rep_list_roles")
async def list_session_roles(
    link: Annotated[SubjectOrganizationLink, Depends(get_current_user)]
) -> set[str]:
    if link.session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return link.session.roles


@router.get("", description="rep_list_subjects")
async def get_subjects_by_organization(
    link: Annotated[SubjectOrganizationLink, Depends(get_current_user)],
    username: str | None = None,
) -> list[SubjectActiveListing]:
    return await crud_subject_organization_link.get_subjects_by_organization(
        link.organization_name, username
    )


@router.get("/role", description="rep_list_subject_roles")
async def list_subject_roles(
    subject: str, link: Annotated[SubjectOrganizationLink, Depends(get_current_user)]
) -> list[str]:
    return await crud_subject_organization_link.get_subject_roles(
        link.organization_name, subject
    )


@router.delete("/session/role", description="rep_drop_role")
async def drop_role(
    role: str, link: Annotated[SubjectOrganizationLink, Depends(get_current_user)]
) -> str:
    return await crud_subject_organization_link.drop_role_from_session(link, role)


@router.delete("/role", description="rep_remove_permission")
async def remove_role_from_subject(
    role: str,
    username: str,
    link: Annotated[
        SubjectOrganizationLink,
        Security(check_permission, scopes=[Permission.ROLE_MOD]),
    ],
) -> set[str]:
    new_link = await crud_subject_organization_link.manage_subject_role(
        link.organization_name, username, role, "remove"
    )
    return new_link.role_ids


@router.patch("/activation/activate", description="rep_activate_subject")
async def activate_subject(
    username: str,
    link: Annotated[
        SubjectOrganizationLink,
        Security(check_permission, scopes=[Permission.SUBJECT_UP]),
    ],
) -> SubjectActiveListing:
    result = await crud_subject_organization_link.set_active(
        username, link.organization_name, True
    )
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Subject not found or not linked to this organization",
        )
    return SubjectActiveListing(
        username=result.subject_username,
        active=result.active,
        full_name=result.subject.full_name,
    )


@router.patch("/activation/suspend", description="rep_suspend_subject")
async def suspend_subject(
    username: str,
    link: Annotated[
        SubjectOrganizationLink,
        Security(check_permission, scopes=[Permission.SUBJECT_DOWN]),
    ],
) -> SubjectActiveListing:
    result = await crud_subject_organization_link.set_active(
        username, link.organization_name, False
    )
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Subject not found or not linked to this organization",
        )
    return SubjectActiveListing(
        username=result.subject_username,
        active=result.active,
        full_name=result.subject.full_name,
    )

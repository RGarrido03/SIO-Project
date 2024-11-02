from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from starlette.responses import Response

from repository.crud.subject import crud_subject
from repository.crud.subject_organization_link import crud_subject_organization_link
from repository.models.permission import RoleEnum
from repository.models.relations import SubjectOrganizationLink
from repository.models.session import Session
from repository.models.subject import SubjectCreate, Subject
from repository.utils.auth.authorization_handler import get_current_user
from repository.utils.auth.generate_token import AuthSessionLogin

router = APIRouter(prefix="/subject", tags=["Subject"])


@router.post("")
async def create_subject(subject: SubjectCreate) -> Subject:
    obj = await crud_subject.create(subject)
    return obj.subject


# AuthSessionLogin equivale a SessionCreate
@router.post("/session")
async def create_session(info: Annotated[AuthSessionLogin, Depends()]) -> Response:
    try:
        token_enc = await crud_subject_organization_link.create_session(info)
        response = Response(content=token_enc, media_type="application/octet-stream")
        response.headers["Content-Disposition"] = "attachment; filename=session"
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/session/role")
async def add_role(
    role: RoleEnum, _: Annotated[SubjectOrganizationLink, Depends(get_current_user)]
) -> Session:
    try:
        link = await crud_subject_organization_link.get_and_verify_session(
            "username", "organization"  # TODO: Get from session
        )
        return await crud_subject_organization_link.add_role_to_session(link, role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/session/role")
async def drop_role(role: RoleEnum) -> Session:
    try:
        link = await crud_subject_organization_link.get_and_verify_session(
            "username", "organization"  # TODO: Get from session
        )
        return await crud_subject_organization_link.drop_role_from_session(link, role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/activation")
async def set_activation(username: str, active: bool) -> Subject | None:
    return await crud_subject.set_active(username, active)

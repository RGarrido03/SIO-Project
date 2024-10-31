from fastapi import APIRouter, HTTPException

from repository.crud.subject import crud_subject
from repository.crud.subject_organization_link import crud_subject_organization_link
from repository.models.session import SessionCreate, Session
from repository.models.subject import SubjectCreate, Subject

router = APIRouter(prefix="/subject", tags=["Subject"])


@router.post("")
async def create_subject(subject: SubjectCreate) -> Subject:
    obj = await crud_subject.create(subject)
    return obj.subject


@router.post("/session")
async def create_session(info: SessionCreate) -> Session:
    try:
        return await crud_subject_organization_link.create_session(info)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/activation")
async def set_activation(username: str, active: bool) -> Subject | None:
    return await crud_subject.set_active(username, active)

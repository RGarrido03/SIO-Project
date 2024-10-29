from fastapi import APIRouter

from repository.crud.subject import crud_subject
from repository.models.subject import SubjectCreate, Subject

router = APIRouter(prefix="/subject", tags=["Subject"])


@router.post("/")
async def create_subject(subject: SubjectCreate) -> Subject:
    return await crud_subject.create(subject)


@router.patch("/activation")
async def set_activation(username: str, active: bool) -> Subject | None:
    return await crud_subject.set_active(username, active)

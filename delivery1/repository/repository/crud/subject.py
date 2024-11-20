from repository.config.database import get_session
from repository.crud.base import CRUDBase
from repository.crud.public_key import crud_public_key
from repository.models.subject import (
    Subject,
    SubjectCreate,
    PublicKeyCreate,
    SubjectWithPublicKeyUUID,
)


class CRUDSubject(CRUDBase[Subject, SubjectCreate, str]):
    def __init__(self) -> None:
        super().__init__(Subject)

    async def create(self, create_obj: SubjectCreate) -> SubjectWithPublicKeyUUID:

        async with get_session() as session:
            # GETTING THE SUBJECT
            if await self.get(create_obj.username) is not None:
                raise ValueError("Subject with this username already exists")
            subject = Subject.model_validate(create_obj)
            subject = await self._add_to_db(subject, session=session)
            public_key = await crud_public_key.create(
                PublicKeyCreate(
                    key=create_obj.public_key, subject_username=subject.username
                )
            )
            await session.refresh(subject)
            return SubjectWithPublicKeyUUID(subject=subject, public_key=public_key)

    async def set_active(self, username: str, active: bool) -> Subject | None:
        user = await self.get(username)
        if user is None:
            return None

        user.active = active
        return await self._add_to_db(user)


crud_subject = CRUDSubject()

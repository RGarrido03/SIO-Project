from repository.config.database import get_session
from repository.crud.base import CRUDBase
from repository.models.subject import Subject, SubjectCreate


class CRUDSubject(CRUDBase[Subject, SubjectCreate, str]):
    def __init__(self) -> None:
        super().__init__(Subject)

    async def set_active(self, username: str, active: bool) -> Subject | None:
        user = await self.get(username)
        if user is None:
            return None

        user.active = active

        session = await anext(get_session())
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


crud_subject = CRUDSubject()

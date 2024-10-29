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
        return await self._add_to_db(user)


crud_subject = CRUDSubject()

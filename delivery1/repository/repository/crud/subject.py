from repository.crud.base import CRUDBase
from repository.models.subject import Subject, SubjectCreate


class CRUDSubject(CRUDBase[Subject, SubjectCreate, str]):
    def __init__(self) -> None:
        super().__init__(Subject)


crud_subject = CRUDSubject()

from repository.crud.base import CRUDBase
from repository.models.relations import (
    SubjectOrganizationLink,
    SubjectOrganizationLinkCreate,
)


class CRUDSubjectOrganizationLink(
    CRUDBase[SubjectOrganizationLink, SubjectOrganizationLinkCreate, tuple[str, str]]
):
    def __init__(self) -> None:
        super().__init__(SubjectOrganizationLink)


crud_subject_organization_link = CRUDSubjectOrganizationLink()

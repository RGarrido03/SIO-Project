import uuid

from repository.crud.base import CRUDBase
from repository.crud.subject_organization_link import crud_subject_organization_link
from repository.models.organization import Organization, OrganizationBase
from repository.models.relations import SubjectOrganizationLinkCreate


class CRUDOrganization(CRUDBase[Organization, OrganizationBase, str]):
    def __init__(self) -> None:
        super().__init__(Organization)

    async def add_subject(
        self, organization_name: str, subject_username: str, public_key_fk: uuid.UUID
    ) -> None:
        await crud_subject_organization_link.create(
            SubjectOrganizationLinkCreate(
                organization_name=organization_name,
                subject_username=subject_username,
                public_key_id=public_key_fk,
            )
        )


crud_organization = CRUDOrganization()

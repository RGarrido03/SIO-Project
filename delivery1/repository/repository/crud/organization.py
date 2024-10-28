from repository.crud.base import CRUDBase
from repository.models.organization import Organization, OrganizationCreate


class CRUDOrganization(CRUDBase[Organization, OrganizationCreate]):
    def __init__(self) -> None:
        super().__init__(Organization)


crud_organization = CRUDOrganization()

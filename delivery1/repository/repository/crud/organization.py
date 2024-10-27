from repository.crud.base import CRUDBase
from repository.models.organization import Organization, OrganizationCreate


class CRUDOrganization(CRUDBase[Organization, OrganizationCreate]):
    pass


crud_organization = CRUDOrganization(Organization)

from repository.crud.base import CRUDBase
from repository.models import OrganizationRole
from repository.models.organization import OrganizationRoleBase


class CRUDOrganizationRole(
    CRUDBase[OrganizationRole, OrganizationRoleBase, tuple[str, str]]
):
    def __init__(self) -> None:
        super().__init__(OrganizationRole)


crud_organization_role = CRUDOrganizationRole()

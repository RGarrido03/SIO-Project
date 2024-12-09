from repository.crud.base import CRUDBase
from repository.crud.organization_role import crud_organization_role
from repository.models.organization import (
    Organization,
    OrganizationBase,
    OrganizationRoleBase,
)
from repository.models.permission import all_permissions


class CRUDOrganization(CRUDBase[Organization, OrganizationBase, str]):
    def __init__(self) -> None:
        super().__init__(Organization)

    async def create(self, obj: OrganizationBase) -> Organization:
        if await self.get(obj.name):
            raise ValueError("Organization with this name already exists")

        db_obj = Organization.model_validate(obj)
        db_obj = await self._add_to_db(db_obj)

        crud_organization_role.create(
            OrganizationRoleBase(
                organization_name=db_obj.name,
                role="Managers",
                permissions=all_permissions,
            )
        )
        return db_obj


crud_organization = CRUDOrganization()

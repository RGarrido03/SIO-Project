from sqlmodel import select

from repository.config.database import get_session
from repository.crud.base import CRUDBase
from repository.models import OrganizationRole
from repository.models.organization import OrganizationRoleBase
from repository.models.permission import Permission


class CRUDOrganizationRole(
    CRUDBase[OrganizationRole, OrganizationRoleBase, tuple[str, str]]
):
    def __init__(self) -> None:
        super().__init__(OrganizationRole)

    async def create(self, obj: OrganizationRoleBase) -> OrganizationRole:
        existing = await self.get((obj.organization_name, obj.role))
        if existing:
            raise ValueError("Role already exists")
        return await super().create(obj)

    async def get_roles_by_permission(
        self, organization_name: str, permission: Permission
    ) -> list[str]:
        async with get_session() as session:
            result = await session.exec(
                select(OrganizationRole)
                .where(OrganizationRole.organization_name == organization_name)
                .where(OrganizationRole.permissions.contains({permission}))
            )
            data: list[OrganizationRole] = list(result.all())
            return [role.role for role in data]


crud_organization_role = CRUDOrganizationRole()

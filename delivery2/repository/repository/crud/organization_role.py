from typing import Literal

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

    async def set_activation(
        self, organization_name: str, role: str, active: bool
    ) -> OrganizationRole:
        role_obj = await self.get((organization_name, role))
        if role_obj is None:
            raise ValueError("Role not found")
        role_obj.active = active
        return await self._add_to_db(role_obj)

    async def set_permission(
        self,
        organization_name: str,
        role: str,
        permission: Permission,
        change: Literal["add", "remove"],
    ) -> OrganizationRole:
        role_obj = await self.get((organization_name, role))
        if role_obj is None:
            raise ValueError("Role not found")
        match change:
            case "add":
                p = set(role_obj.permissions)
                p.add(permission)
                role_obj.permissions = p
            case "remove":
                p = set(role_obj.permissions)
                p.discard(permission)
                role_obj.permissions = p
        return await self._add_to_db(role_obj)


crud_organization_role = CRUDOrganizationRole()

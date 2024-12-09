from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from repository.crud.organization_role import crud_organization_role
from repository.models import SubjectOrganizationLink
from repository.models.organization import OrganizationRoleBase, OrganizationRole
from repository.models.permission import Permission
from repository.utils.auth.authorization_handler import get_current_user

router = APIRouter(prefix="/role", tags=["Role"])


@router.post("", description="rep_add_role")
async def add_role(
    role: str,
    link: Annotated[SubjectOrganizationLink, Depends(get_current_user)],
) -> OrganizationRole:
    try:
        return await crud_organization_role.create(
            OrganizationRoleBase(
                organization_name=link.organization_name,
                role=role,
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/permission", description="rep_list_role_permissions")
async def list_role_permissions(
    role: str, link: Annotated[SubjectOrganizationLink, Depends(get_current_user)]
) -> list[str]:
    role_obj = await crud_organization_role.get((link.organization_name, role))
    if role_obj is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role_obj.permissions


@router.get("", description="rep_list_permission_roles")
async def list_roles_by_permission(
    permission: Permission,
    link: Annotated[SubjectOrganizationLink, Depends(get_current_user)],
) -> list[str]:
    return await crud_organization_role.get_roles_by_permission(
        link.organization_name, permission
    )

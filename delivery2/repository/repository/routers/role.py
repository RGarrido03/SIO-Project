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


@router.post("/activation", description="rep_reactivate_role")
async def activate_role(
    role: str,
    link: Annotated[SubjectOrganizationLink, Depends(get_current_user)],
) -> OrganizationRole:
    try:
        return await crud_organization_role.set_activation(
            link.organization_name, role, True
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/permission", description="rep_add_permission")
async def add_permission_to_role(
    role: str,
    permission: Permission,
    link: Annotated[SubjectOrganizationLink, Depends(get_current_user)],
) -> OrganizationRole:
    try:
        return await crud_organization_role.set_permission(
            link.organization_name, role, permission, "add"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", description="rep_list_permission_roles")
async def list_roles_by_permission(
    permission: Permission,
    link: Annotated[SubjectOrganizationLink, Depends(get_current_user)],
) -> list[str]:
    return await crud_organization_role.get_roles_by_permission(
        link.organization_name, permission
    )


@router.get("/permission", description="rep_list_role_permissions")
async def list_role_permissions(
    role: str, link: Annotated[SubjectOrganizationLink, Depends(get_current_user)]
) -> list[str]:
    role_obj = await crud_organization_role.get((link.organization_name, role))
    if role_obj is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role_obj.permissions


@router.delete("/activation", description="rep_suspend_role")
async def suspend_role(
    role: str,
    link: Annotated[SubjectOrganizationLink, Depends(get_current_user)],
) -> OrganizationRole:
    try:
        return await crud_organization_role.set_activation(
            link.organization_name, role, False
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/permission", description="rep_remove_permission")
async def remove_permission_from_role(
    role: str,
    permission: Permission,
    link: Annotated[SubjectOrganizationLink, Depends(get_current_user)],
) -> OrganizationRole:
    try:
        return await crud_organization_role.set_permission(
            link.organization_name, role, permission, "remove"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

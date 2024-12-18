from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security

from repository.crud.document import crud_document
from repository.crud.organization_role import crud_organization_role
from repository.crud.subject_organization_link import crud_subject_organization_link
from repository.models.document import DocumentRolesByPermission
from repository.models.organization import OrganizationRoleBase, OrganizationRole
from repository.models.permission import Permission, DocumentPermission
from repository.models.relations import SubjectOrganizationLink
from repository.models.subject import SubjectActiveListing
from repository.utils.auth.authorization_handler import (
    get_current_user,
    check_permission,
)

router = APIRouter(prefix="/role", tags=["Role"])


@router.post("", description="rep_add_role")
async def add_role(
    role: str,
    link: Annotated[
        SubjectOrganizationLink,
        Security(check_permission, scopes=[Permission.ROLE_NEW]),
    ],
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


@router.post("/permission", description="rep_add_permission")
async def add_permission_to_role(
    role: str,
    permission: Permission,
    link: Annotated[
        SubjectOrganizationLink,
        Security(check_permission, scopes=[Permission.ROLE_MOD]),
    ],
) -> OrganizationRole:
    try:
        return await crud_organization_role.set_permission(
            link.organization_name, role, permission, "add"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", description="rep_list_permission_roles")
async def list_roles_by_permission(
    permission: Permission | DocumentPermission,
    link: Annotated[SubjectOrganizationLink, Depends(get_current_user)],
) -> list[str] | list[DocumentRolesByPermission]:
    if isinstance(permission, DocumentPermission):
        return await crud_document.get_roles_by_permission(
            link.organization_name, permission
        )

    return await crud_organization_role.get_roles_by_permission(
        link.organization_name, permission
    )


@router.get("/permission", description="rep_list_role_permissions")
async def list_role_permissions(
    role: str, link: Annotated[SubjectOrganizationLink, Depends(get_current_user)]
) -> set[Permission]:
    role_obj = await crud_organization_role.get((link.organization_name, role))
    if role_obj is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role_obj.permissions


@router.get("/subject", description="rep_list_role_subjects")
async def list_subjects_by_role(
    role: str, link: Annotated[SubjectOrganizationLink, Depends(get_current_user)]
) -> list[SubjectActiveListing]:
    try:
        return await crud_subject_organization_link.get_subjects_by_role(
            link.organization_name, role
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/activation/activate", description="rep_reactivate_role")
async def activate_role(
    role: str,
    link: Annotated[
        SubjectOrganizationLink, Security(check_permission, scopes=[Permission.ROLE_UP])
    ],
) -> OrganizationRole:
    try:
        return await crud_organization_role.set_activation(
            link.organization_name, role, True
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/activation/suspend", description="rep_suspend_role")
async def suspend_role(
    role: str,
    link: Annotated[
        SubjectOrganizationLink,
        Security(check_permission, scopes=[Permission.ROLE_DOWN]),
    ],
) -> OrganizationRole:
    try:
        if role == "Managers":
            raise ValueError("Cannot suspend Managers role")
        return await crud_organization_role.set_activation(
            link.organization_name, role, False
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/permission", description="rep_remove_permission")
async def remove_permission_from_role(
    role: str,
    permission: Permission,
    link: Annotated[
        SubjectOrganizationLink,
        Security(check_permission, scopes=[Permission.ROLE_MOD]),
    ],
) -> OrganizationRole:
    try:
        return await crud_organization_role.set_permission(
            link.organization_name, role, permission, "remove"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

from datetime import datetime
from typing import Annotated, cast

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt import InvalidTokenError
from sqlalchemy import func
from sqlmodel import select

from repository.config.database import get_session
from repository.config.settings import settings
from repository.crud.subject import crud_subject
from repository.crud.subject_organization_link import crud_subject_organization_link
from repository.models import OrganizationRole
from repository.models.permission import DocumentPermission
from repository.models.relations import SubjectOrganizationLink
from repository.models.session import Session
from repository.utils.exceptions import (
    credentials_exception,
    inactive_user_exception,
    session_expired_exception,
    no_session_exception,
    not_enough_permissions_exception,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/subject/session")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> SubjectOrganizationLink:
    try:
        payload = jwt.decode(
            token, settings.AUTH_SECRET_KEY, algorithms=[settings.AUTH_ALGORITHM]
        )
        username: str = payload.get("username")
        organization: str = payload.get("organization")
    except jwt.exceptions.ExpiredSignatureError:
        raise session_expired_exception
    except InvalidTokenError:
        raise credentials_exception

    subject = await crud_subject.get(username)
    if subject is None:
        raise credentials_exception

    link = await crud_subject_organization_link.get((username, organization))
    if link is None:
        raise credentials_exception
    if not link.active:
        raise inactive_user_exception
    if link.session is None:
        raise no_session_exception
    if link.session.expires < datetime.now():
        raise session_expired_exception
    if str(link.session.id) != payload.get("sub"):
        raise credentials_exception
    return link


async def check_permission(
    security_scopes: SecurityScopes,
    link: Annotated[SubjectOrganizationLink, Depends(get_current_user)],
) -> SubjectOrganizationLink:
    session = cast(Session, link.session)  # Session is never None in this context

    async with get_session() as db_session:
        permissions = await db_session.exec(
            select(func.unnest(OrganizationRole.permissions))
            .where(OrganizationRole.organization_name == link.organization_name)
            .where(OrganizationRole.role.in_(session.roles))
        )
        permissions_in_session = set(permissions.all())

    if any(
        permission not in permissions_in_session
        for permission in security_scopes.scopes
    ):
        raise not_enough_permissions_exception

    return link


def check_doc_permission(
    permission: DocumentPermission,
    acl: dict[str, set[DocumentPermission]],
    roles: set[str],
) -> None:
    permissions = set(
        [p for role, p_set in acl.items() for p in p_set if role in roles]
    )
    if permission not in permissions:
        raise not_enough_permissions_exception

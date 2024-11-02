from datetime import datetime
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from starlette import status

from repository.config.settings import settings
from repository.crud.subject import crud_subject
from repository.crud.subject_organization_link import crud_subject_organization_link
from repository.models.relations import SubjectOrganizationLink

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/subject/session")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> SubjectOrganizationLink:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.AUTH_SECRET_KEY, algorithms=[settings.AUTH_ALGORITHM]
        )
        username: str = payload.get("username")
        organization: str = payload.get("organization")
    except InvalidTokenError:
        raise credentials_exception

    subject = await crud_subject.get(username)
    if subject is None:
        raise credentials_exception
    if not subject.active:
        raise HTTPException(status_code=400, detail="Inactive user")

    link = await crud_subject_organization_link.get((username, organization))
    if link is None:
        raise credentials_exception
    if link.session is None:
        raise credentials_exception
    if link.session.expires < datetime.now():
        raise HTTPException(status_code=400, detail="Session expired")
    return link

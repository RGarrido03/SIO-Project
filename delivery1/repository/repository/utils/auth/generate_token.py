from typing import Annotated

import jwt
from fastapi import Form, UploadFile
from fastapi.security import OAuth2PasswordRequestForm

from repository.config.settings import settings
from repository.models.session import SessionWithSubjectInfo


class AuthSessionLogin(OAuth2PasswordRequestForm):
    def __init__(
        self,
        organization: Annotated[
            str,
            Form(),
        ],
        username: Annotated[
            str,
            Form(),
        ],
        password: Annotated[
            str,
            Form(),
        ],
        credentials: UploadFile,
    ):
        super().__init__(username=username, password=password)
        self.organization = organization
        self.credentials = credentials


def create_token(session: SessionWithSubjectInfo) -> str:
    payload = {
        "sub": str(session.id),
        "username": session.username,
        "organization": session.organization,
        "exp": session.expires,
        "roles": list(session.roles),
        "keys": session.keys,
    }
    return jwt.encode(
        payload, settings.AUTH_SECRET_KEY, algorithm=settings.AUTH_ALGORITHM
    )

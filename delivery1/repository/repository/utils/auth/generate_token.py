import jwt

from repository.config.settings import settings
from repository.models.session import SessionWithSubjectInfo


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

from fastapi import HTTPException
from starlette import status

hmac_exception = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail="HMAC does not match",
)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

inactive_user_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Inactive user",
)

no_session_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No session created",
)

session_expired_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Session expired",
)

not_enough_permissions_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not enough permissions",
)

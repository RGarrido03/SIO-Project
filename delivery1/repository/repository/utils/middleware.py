from typing import Any

import jwt
from fastapi import Request

from repository.config.settings import settings
from repository.utils.encryption.encryptors import decrypt_asymmetric, decrypt_symmetric


async def decrypt_request_token(request: Request) -> Request:
    if request.headers.get("Encryption") != "session":
        return request

    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        return request

    token = decrypt_asymmetric(auth_header.encode(), settings.KEYS[0])

    headers = dict(request.scope["headers"])
    headers[b"Authorization"] = token
    request.scope["headers"] = [(k, v) for k, v in headers.items()]

    return request


async def decrypt_request_body(request: Request) -> Request:
    data = await request.body()
    if not data:
        return request

    match request.headers.get("Encryption"):
        case "repository":
            data = decrypt_asymmetric(data, settings.KEYS[0])
        case "session":
            auth_header = request.headers.get("Authorization")
            if auth_header is None:
                return request

            payload: dict[str, Any] = jwt.decode(
                auth_header,
                settings.AUTH_SECRET_KEY,
                algorithms=[settings.AUTH_ALGORITHM],
            )
            key: str = payload.get("keys", [])[0]
            data = decrypt_symmetric(data, key.encode())
        case _:
            return request

    request._body = data
    return request

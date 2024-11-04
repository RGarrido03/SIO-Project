import base64
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

    auth_bytes = base64.decodebytes(auth_header.encode())
    token = decrypt_asymmetric(auth_bytes, settings.KEYS[0])

    headers = dict(request.scope["headers"])
    headers[b"Authorization"] = token
    request.scope["headers"] = [(k, v) for k, v in headers.items()]

    return request


async def decrypt_request_body(request: Request) -> Request:
    data = await request.body()
    data = base64.decodebytes(data)
    if not data:
        return request

    print("pixola", data)

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

    print("pixa", data)
    request._body = data
    return request

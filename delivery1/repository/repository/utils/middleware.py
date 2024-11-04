import base64
from typing import Any

import jwt
from fastapi import Request

from repository.config.settings import settings
from repository.utils.encryption.encryptors import decrypt_asymmetric, decrypt_symmetric


async def decrypt_request_key(request: Request) -> bytes | None:
    if (encryption := request.headers.get("Encryption")) is None:
        return None

    if (auth_header := request.headers.get("Authorization")) is None:
        return None

    match encryption:
        case "repository":
            auth_header_bytes = (
                auth_header.encode().replace(b"\\n", b"\n").replace(b"\\r", b"\r")
            )
            return decrypt_asymmetric(
                base64.decodebytes(auth_header_bytes), settings.KEYS[0]
            )
        case "session":
            payload: dict[str, Any] = jwt.decode(
                auth_header,
                settings.AUTH_SECRET_KEY,
                algorithms=[settings.AUTH_ALGORITHM],
            )
            return payload.get("keys", [])[0].encode()
        case _:
            return None


async def decrypt_request_body(request: Request, token: bytes | None) -> Request:
    if token is None:
        return request

    data = await request.body()
    if not data:
        return request

    match request.headers.get("Encryption"):
        case "repository":
            data = base64.decodebytes(data)
            data = decrypt_symmetric(data, token)
        case "session":
            payload: dict[str, Any] = jwt.decode(
                token.decode(),
                settings.AUTH_SECRET_KEY,
                algorithms=[settings.AUTH_ALGORITHM],
            )
            key: str = payload.get("keys", [])[0]
            data = decrypt_symmetric(data, key.encode())
        case _:
            return request

    request._body = data
    return request

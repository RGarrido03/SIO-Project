import base64
from typing import Any

import jwt
from fastapi import Request

from repository.config.settings import settings
from repository.utils.encryption.encryptors import decrypt_asymmetric, decrypt_symmetric


async def decrypt_request_key(request: Request) -> tuple[Request, bytes | None]:
    if (encryption := request.headers.get("Encryption")) is None:
        return request, None

    if (auth_header := request.headers.get("Authorization")) is None:
        return request, None

    auth_header_bytes = (
        auth_header.encode().replace(b"\\n", b"\n").replace(b"\\r", b"\r")
    )
    token = decrypt_asymmetric(base64.decodebytes(auth_header_bytes), settings.KEYS[0])

    headers = dict(request.scope["headers"])
    headers[b"authorization"] = b"Bearer " + token if encryption == "session" else token
    request.scope["headers"] = [(k, v) for k, v in headers.items()]

    if encryption != "session":
        return request, token

    payload: dict[str, Any] = jwt.decode(
        token,
        settings.AUTH_SECRET_KEY,
        algorithms=[settings.AUTH_ALGORITHM],
    )
    return request, payload.get("keys", [])[0].encode()


async def decrypt_request_body(request: Request, token: bytes | None) -> None:
    if token is None:
        return

    if (iv_header := request.headers.get("IV")) is None:
        return

    iv = base64.decodebytes(iv_header.encode())
    data = await request.body()
    if not data:
        return

    match request.headers.get("Encryption"):
        case "repository":
            data = base64.decodebytes(data)
            data = decrypt_symmetric(data, token, iv)
        case "session":
            payload: dict[str, Any] = jwt.decode(
                token.decode(),
                settings.AUTH_SECRET_KEY,
                algorithms=[settings.AUTH_ALGORITHM],
            )
            key: str = payload.get("keys", [])[0]
            data = decrypt_symmetric(data, key.encode(), iv)
        case _:
            return

    request._body = data

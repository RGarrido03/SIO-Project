import base64
import os
from typing import Any, AsyncIterable

import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import Request
from starlette.middleware.base import _StreamingResponse
from starlette.responses import Response

from repository.config.settings import settings
from repository.utils.encoding import b64_encode_and_escape, b64_decode_and_unescape
from repository.utils.encryption.encryptors import (
    decrypt_asymmetric,
    decrypt_symmetric,
    encrypt_symmetric,
    encrypt_asymmetric,
)


async def decrypt_request_key(request: Request) -> tuple[Request, bytes | None]:
    if (encryption := request.headers.get("Encryption")) is None:
        return request, None

    if (auth_header := request.headers.get("Authorization")) is None:
        return request, None

    auth_header_bytes = b64_decode_and_unescape(auth_header)
    token = decrypt_asymmetric(auth_header_bytes, settings.KEYS[0])

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


async def encrypt_response(response: Response, public_key: RSAPublicKey) -> None:
    key = os.urandom(16)
    iv = os.urandom(16)

    if isinstance(response, _StreamingResponse):
        body = b"".join([x async for x in response.body_iterator])  # type: ignore
        body_enc = encrypt_symmetric(body, key, iv)
        body_enc = base64.encodebytes(body_enc)

        async def new_body_iterator() -> AsyncIterable[bytes]:
            yield body_enc

        response.body_iterator = new_body_iterator()
    else:
        body = response.body
        body_enc = encrypt_symmetric(body, key, iv)
        response.body = body_enc

    key_enc = encrypt_asymmetric(key, public_key)

    response.headers["Content-Length"] = str(len(body_enc))
    response.headers["IV"] = b64_encode_and_escape(iv)
    response.headers["Authorization"] = b64_encode_and_escape(key_enc)

import base64
import json
import os
from typing import Any, AsyncIterable

import jwt
from fastapi import Request
from starlette.datastructures import State
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
        verify=False,
        options={"verify_signature": False},
    )
    request.state.session_key = payload.get("keys", [])[0].encode()
    return request, payload.get("keys", [])[0].encode()


async def decrypt_request_url(request: Request, token: bytes | None) -> None:
    if token is None:
        return

    if (iv_header := request.headers.get("IV")) is None:
        return

    if request.headers.get("Encryption") is None:
        return

    iv = base64.decodebytes(iv_header.encode())

    url = base64.decodebytes(
        request.url.path.encode()
        .replace(b"\\n", b"\n")
        .replace(b"\\r", b"\r")
        .lstrip(b"/")
    )

    url_unenc = decrypt_symmetric(url, token, iv).decode()
    path, query = url_unenc.split("?", 1) if "?" in url_unenc else (url_unenc, "")
    request._url = request._url.replace(path=path)
    request.scope["path"] = "/" + path
    request.scope["query_string"] = query.encode()


async def decrypt_request_body(request: Request, token: bytes | None) -> None:
    if token is None:
        return

    if (iv_header := request.headers.get("IV")) is None:
        return

    iv = base64.decodebytes(iv_header.encode())
    data = await request.body()
    if not data:
        return

    if request.headers.get("Encryption") is None:
        return

    data = base64.decodebytes(data)
    data = decrypt_symmetric(data, token, iv)

    request._body = data


async def _get_response_body(response: Response) -> bytes:
    if isinstance(response, _StreamingResponse):
        return b"".join([x async for x in response.body_iterator])  # type: ignore
    return response.body


async def _set_response_body(response: Response, body: bytes) -> None:
    async def new_body_iterator() -> AsyncIterable[bytes]:
        yield body

    if isinstance(response, _StreamingResponse):
        response.body_iterator = new_body_iterator()
        return
    response.body = body


async def obfuscate_response(response: Response) -> None:
    body = await _get_response_body(response)

    new_body = {
        "code": response.status_code,
        "data": body.decode(),
    }
    body_enc = json.dumps(new_body).encode()
    await _set_response_body(response, body_enc)
    response.status_code = 200
    response.headers["Content-Length"] = str(len(body_enc))


async def encrypt_response(
    response: Response,
    state: State,
    encrypt: bool,
) -> None:
    if not encrypt:
        return

    iv = os.urandom(16)
    try:
        public_key = state.public_key
    except AttributeError:
        public_key = None

    try:
        key = state.session_key
    except AttributeError:
        key = os.urandom(16)

    body = await _get_response_body(response)
    body_enc = encrypt_symmetric(body, key, iv)
    body_enc = base64.encodebytes(body_enc)
    await _set_response_body(response, body_enc)

    if public_key is not None:
        key_enc = encrypt_asymmetric(key, public_key)
        response.headers["Authorization"] = b64_encode_and_escape(key_enc)

    response.headers["Content-Length"] = str(len(body_enc))
    response.headers["IV"] = b64_encode_and_escape(iv)

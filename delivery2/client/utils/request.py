import json
import time
from typing import Literal, Any

import jwt
import requests
import typer
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

from utils.encoding import b64_decode_and_unescape
from utils.encryption.encryptors import (
    encrypt_request,
    decrypt_asymmetric,
    decrypt_symmetric,
)


def request_without_session_repo(
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
    repository_address: str,
    url: str,
    obj: dict[str, Any],
    private_key: RSAPrivateKey | None,
    repository_public_key: RSAPublicKey,
    content_type: str = "application/json",
    params: dict[str, str] | None = None,
) -> tuple[str, requests.Response]:
    (url, req_key, req_data, req_iv) = encrypt_request(
        url, obj, repository_public_key, params=params
    )

    response = requests.request(
        method,
        repository_address + "/" + url,
        data=req_data,
        headers={
            "Content-Type": content_type,
            "Encryption": "repository",
            "IV": req_iv,
            "Authorization": req_key,
        },
    )

    if response.status_code != 200 and response.status_code != 201:
        try:
            msg = json.loads(response.content)
            print(msg["detail"])
        except:
            print(response.content)
        raise typer.Exit(code=-1)

    if "Authorization" not in response.headers or private_key is None:
        return response.content.decode(), response

    res_iv = b64_decode_and_unescape(response.headers["IV"])
    res_key = decrypt_asymmetric(
        b64_decode_and_unescape(response.headers["Authorization"]),
        private_key,
    )

    return decrypt_symmetric(response.content, res_key, res_iv).decode(), response


def request_with_session(
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
    repository_address: str,
    url: str,
    obj: dict[str, Any] | None,
    session: bytes,
    repository_public_key: RSAPublicKey,
    content_type: str = "application/json",
    params: dict[str, str | bool] | None = None,
) -> tuple[str, requests.Response]:
    payload = jwt.decode(
        session, algorithms=["HS256"], options={"verify_signature": False}
    )
    if payload["exp"] < time.time():
        print("Session expired, please create a new one.")
        raise typer.Exit(code=1)

    (url, req_key, req_data, req_iv) = encrypt_request(
        url,
        obj,
        repository_public_key,
        key=session,
        payload=payload,
        params=params,
    )
    response = requests.request(
        method,
        repository_address + "/" + url,
        data=req_data,
        headers={
            "Content-Type": content_type,
            "Encryption": "session",
            "IV": req_iv,
            "Authorization": req_key,
        },
    )

    if response.status_code == 500:
        msg = json.loads(response.content)
        print(msg["detail"])
        raise typer.Exit(code=-1)

    if "IV" not in response.headers:
        return response.content.decode(), response

    res_iv = b64_decode_and_unescape(response.headers["IV"])

    dec_body = decrypt_symmetric(
        response.content, payload["keys"][0].encode(), res_iv
    ).decode()

    if 400 <= response.status_code < 500:
        print(dec_body)
        raise typer.Exit(code=-1)

    return dec_body, response

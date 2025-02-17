import hmac
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


def request_without_encryption(
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
    repository_address: str,
    url: str,
    obj: dict[str, Any] | None = None,
    content_type: str = "application/json",
    params: dict[str, str] | None = None,
) -> tuple[str, requests.Response]:

    response = requests.request(
        method,
        repository_address + "/" + url,
        json=obj,
        headers={"Content-Type": content_type},
        params=params,
    )

    body = response.content.decode()
    body_dict = json.loads(body)
    code = body_dict.get("code")
    data = body_dict.get("data")

    if code != 200 and code != 201:
        try:
            msg = json.loads(data)
            print(msg["detail"])
        except:
            print(data)
        raise typer.Exit(code=-1)

    return data, response


def request_without_session_repo(
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
    repository_address: str,
    url: str,
    obj: dict[str, Any] | None,
    private_key: RSAPrivateKey | None,
    repository_public_key: RSAPublicKey,
    content_type: str = "application/json",
    params: dict[str, str] | None = None,
) -> tuple[str, requests.Response]:
    (url, req_key, req_data, req_iv, key) = encrypt_request(
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

    body = b64_decode_and_unescape(response.content)

    if len(body) < 32:
        return response.content.decode(), response

    data, hmac_bytes = body[:-32], body[-32:]

    if not hmac.compare_digest(hmac.digest(key, data, "sha256"), hmac_bytes):
        print("HMAC verification failed.")
        raise typer.Exit(code=-1)

    if "IV" in response.headers:
        res_iv = b64_decode_and_unescape(response.headers["IV"].encode())
        res_key = key
        if "Authorization" in response.headers and private_key is not None:
            res_key = decrypt_asymmetric(
                b64_decode_and_unescape(response.headers["Authorization"].encode()),
                private_key,
            )
        body = decrypt_symmetric(data, res_key, res_iv).decode()

    body_dict = json.loads(body)
    code = body_dict.get("code")
    data = body_dict.get("data")

    if code != 200 and code != 201:
        try:
            msg = json.loads(data)
            print(msg["detail"])
        except:
            print(data)
        raise typer.Exit(code=-1)

    return data, response


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

    (url, req_key, req_data, req_iv, key) = encrypt_request(
        url,
        obj,
        repository_public_key,
        key=payload["keys"][0].encode(),
        jwt=session,
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

    res_iv = b64_decode_and_unescape(response.headers["IV"].encode())

    data = b64_decode_and_unescape(response.content)

    if len(data) < 32:
        return response.content.decode(), response

    data, hmac_bytes = data[:-32], data[-32:]

    if not hmac.compare_digest(hmac.digest(key, data, "sha256"), hmac_bytes):
        print("HMAC verification failed.")
        raise typer.Exit(code=-1)

    dec_body = decrypt_symmetric(data, payload["keys"][0].encode(), res_iv).decode()

    body_dict = json.loads(dec_body)
    data = body_dict.get("data")

    if 400 <= body_dict["code"] < 500:
        try:
            msg = json.loads(data)
            if "detail" not in msg:
                raise Exception()
            print(msg["detail"])
        except:
            print(data)
        raise typer.Exit(code=-1)

    return data, response

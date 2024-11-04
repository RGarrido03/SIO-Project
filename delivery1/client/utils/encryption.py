import base64
import json
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.asymmetric.types import (
    PublicKeyTypes,
)
from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher

from utils.repository_info import get_repository_public_key


def load_private_key(
    private_key: bytes, password: str | None = None
) -> tuple[RSAPrivateKey, RSAPublicKey]:
    pk = serialization.load_ssh_private_key(
        private_key, password=password.encode() if password else None
    )
    if not isinstance(pk, RSAPrivateKey):
        raise ValueError("Invalid private key")
    return pk, pk.public_key()


def load_public_key(public_key: str) -> PublicKeyTypes:
    return serialization.load_pem_public_key(public_key.encode())


def encrypt_symmetric(data: bytes, key: bytes, iv: bytes) -> bytes:
    algorithm = algorithms.AES(key)
    mode = modes.CTR(iv)
    encryptor = Cipher(algorithm, mode).encryptor()

    data = encryptor.update(data) + encryptor.finalize()
    return base64.encodebytes(data)


def encrypt_asymmetric(data: bytes, public_key: RSAPublicKey) -> bytes:
    data = public_key.encrypt(data, padding.PKCS1v15())
    return base64.encodebytes(data)


def encrypt_dict(
    data: dict[str, Any],
    public_key: RSAPublicKey = get_repository_public_key(),
) -> bytes:
    return encrypt_asymmetric(json.dumps(data).encode(), public_key)


def decrypt_symmetric(data: bytes, key: bytes, iv: bytes) -> bytes:
    data = base64.decodebytes(data)
    algorithm = algorithms.AES(key)
    mode = modes.CTR(iv)
    decryptor = Cipher(algorithm, mode).decryptor()

    return decryptor.update(data) + decryptor.finalize()


def decrypt_asymmetric(data: bytes, private_key: RSAPrivateKey) -> bytes:
    data = base64.decodebytes(data)
    return private_key.decrypt(data, padding.PKCS1v15())

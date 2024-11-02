from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.asymmetric.types import (
    PublicKeyTypes,
    PrivateKeyTypes,
)


def load_private_key(
    private_key: bytes, password: str | None = None
) -> tuple[PrivateKeyTypes, PublicKeyTypes]:
    pk = serialization.load_ssh_private_key(
        private_key, password=password.encode() if password else None
    )
    return pk, pk.public_key()


def load_public_key(public_key: str) -> PublicKeyTypes:
    return serialization.load_pem_public_key(public_key.encode())


def encrypt(data: bytes, public_key: RSAPublicKey) -> bytes:
    return public_key.encrypt(data, padding.PKCS1v15())


def decrypt(data: bytes, private_key: RSAPrivateKey) -> bytes:
    return private_key.decrypt(data, padding.PKCS1v15())

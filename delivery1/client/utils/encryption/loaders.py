import typer
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.asymmetric.types import (
    PublicKeyTypes,
)


def load_private_key(
    private_key: bytes, password: str | None = None
) -> tuple[RSAPrivateKey, RSAPublicKey]:
    pk = serialization.load_pem_private_key(
        private_key, password=password.encode() if password else None
    )
    if not isinstance(pk, RSAPrivateKey):
        print("Invalid private key")
        raise typer.Exit(code=1)
    return pk, pk.public_key()


def load_public_key(public_key: str) -> PublicKeyTypes:
    try:
        return serialization.load_pem_public_key(public_key.encode())
    except ValueError:
        print("Invalid public key")
        raise typer.Exit(code=1)

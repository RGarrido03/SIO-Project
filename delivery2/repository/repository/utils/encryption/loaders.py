from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey


def load_private_key(
    private_key: bytes, password: str | None = None
) -> tuple[RSAPrivateKey, RSAPublicKey]:
    pk = serialization.load_pem_private_key(
        private_key, password=password.encode() if password else None
    )
    if not isinstance(pk, RSAPrivateKey):
        raise ValueError("Invalid private key")
    return pk, pk.public_key()


def load_public_key(public_key: str) -> RSAPublicKey:
    key = serialization.load_pem_public_key(public_key.encode())
    if not isinstance(key, RSAPublicKey):
        raise ValueError("Invalid public key type (expected RSA)")
    return key

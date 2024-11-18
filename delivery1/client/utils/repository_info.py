import base64

import requests
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from utils.consts import REPOSITORY_URL
from utils.encryption.loaders import load_public_key
from utils.storage import get_storage_dir


def _fetch_repository_public_key() -> str:
    response = requests.get(f"{REPOSITORY_URL}/public_key")
    data = response.text
    return "\n".join(data.strip('"').split("\\n"))


def _fetch_repository_iv() -> bytes:
    response = requests.get(f"{REPOSITORY_URL}/iv")
    data = response.text
    return base64.decodebytes(data.encode())


def get_repository_public_key() -> RSAPublicKey:
    file = get_storage_dir() / "repository" / "public_key.pem"

    if file.exists():
        with open(file, "r") as f:
            return load_public_key(f.read())

    public = _fetch_repository_public_key()
    with open(file, "w+") as f:
        f.write(public)
    return load_public_key(public)

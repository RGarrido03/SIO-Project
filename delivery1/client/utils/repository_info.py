from pathlib import Path

import requests
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from utils.encryption.loaders import load_public_key


def _fetch_repository_public_key() -> str:
    response = requests.get("http://localhost:8000/repository/public")
    return response.text


def get_repository_public_key() -> RSAPublicKey:
    file = Path(__file__).parent.parent / "storage" / "repository" / "public_key.pem"

    if file.exists():
        with open(file, "r") as f:
            return load_public_key(f.read())

    public = "\n".join(_fetch_repository_public_key().strip('"').split("\\n"))
    with open(file, "w+") as f:
        f.write(public)
    return load_public_key(public)

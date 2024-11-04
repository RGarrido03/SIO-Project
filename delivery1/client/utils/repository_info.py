from pathlib import Path

import requests
import typer
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from utils.encryption import load_public_key


def _fetch_repository_public_key() -> str:
    response = requests.get("http://localhost:8000/repository/public")
    return response.text


def get_repository_public_key() -> RSAPublicKey:
    file = (
        Path(typer.get_app_dir("SIO Project - Client"))
        / "storage"
        / "repository"
        / "public_key.pem"
    )

    if file.exists():
        with open(file, "r") as f:
            return load_public_key(f.read())

    public = _fetch_repository_public_key()
    with open(file, "w") as f:
        f.write(public)
    return load_public_key(public)

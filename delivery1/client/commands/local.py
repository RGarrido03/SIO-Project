from pathlib import Path

import typer
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

app = typer.Typer()


@app.command("rep_subject_credentials")
def generate_credentials(password: str, credentials_file: Path) -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    encrypted_pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode()),
    )

    pem_public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.PKCS1,
    )

    if not credentials_file.parent.exists():
        credentials_file.parent.mkdir(parents=True)

    with credentials_file.open("wb+") as f:
        f.write(encrypted_pem_private_key)

    with credentials_file.with_suffix(".pub").open("wb+") as f:
        f.write(pem_public_key)

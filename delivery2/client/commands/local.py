import base64
import json
from hashlib import sha256
from pathlib import Path

import typer
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from utils.encryption.encryptors import decrypt_symmetric

app = typer.Typer()


@app.command("rep_subject_credentials")
def generate_credentials(password: str, credentials_file: Path) -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)

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

    # NEVER FAILS
    # return typer.Exit(code=0)


# rep_decrypt_file <encrypted file> <encryption metadata>
@app.command("rep_decrypt_file")
def decrypt_file(encrypted_file: Path, encryption_metadata: Path) -> bytes:
    with encrypted_file.open("rb") as f:
        encrypted_data = f.read()

    with encryption_metadata.open("r") as f:
        metadata = json.load(f)

    # check integrity of  file
    mic = sha256(base64.encodebytes(encrypted_data)).hexdigest()
    # print(mic)

    if metadata["file_handle"] != mic:
        print("File integrity check failed")
        raise typer.Exit(code=1)

    # TODO
    if metadata["alg"] != "AES":
        print("Unsupported algorithm")
        raise typer.Exit(code=1)

    key = base64.decodebytes(metadata["key"].encode())
    iv = base64.decodebytes(metadata["iv"].encode())

    data = decrypt_symmetric(encrypted_data, key, iv)

    with encrypted_file.with_suffix(".dec").open("wb+") as f:
        f.write(data)

    print(f"File saved as {encrypted_file.with_suffix('.dec')}")

    return data

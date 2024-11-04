import base64
from pathlib import Path

import requests
import typer

from utils.consts import ORGANIZATION_URL, SUBJECT_URL
from utils.encryption.encryptors import encrypt_dict, decrypt_asymmetric
from utils.encryption.loaders import load_private_key
from utils.storage import get_storage_dir

app = typer.Typer()


@app.command("rep_create_org")
def create_organization(
    organization: str,
    username: str,
    name: str,
    email: str,
    public_key_file: Path,
):
    with public_key_file.open() as f:
        public_key = f.read()

    obj = {
        "organization": {"name": organization},
        "subject": {
            "username": username,
            "full_name": name,
            "email": email,
            "public_key": public_key,
        },
    }

    (key, data) = encrypt_dict(obj)

    response = requests.post(
        ORGANIZATION_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Encryption": "repository",
            "Authorization": key,
        },
    )
    body = response.json()
    print(f"Created organization {body['name']}")


@app.command("rep_list_orgs")
def list_organizations():
    response = requests.get(ORGANIZATION_URL)
    body = response.json()
    print("Organizations:")
    for org in body:
        print(" - " + org["name"])


@app.command("rep_create_session")
def create_session(
    organization: str,
    username: str,
    password: str,
    private_key_file: Path,
    session_file: Path | None = None,
):
    with private_key_file.open() as f:
        private_key = f.read()

    obj: dict[str, str] = {
        "organization": organization,
        "username": username,
        "password": password,
        "credentials": base64.encodebytes(private_key.encode()).decode(),
    }
    (key, data) = encrypt_dict(obj)

    response = requests.post(
        f"{SUBJECT_URL}/session",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Encryption": "repository",
            "Authorization": key,
        },
    )

    private = load_private_key(private_key.encode(), password)[0]
    token = decrypt_asymmetric(response.content, private).decode()

    session_file = (
        session_file or get_storage_dir() / "sessions" / organization / "username.txt"
    )

    if not session_file.parent.exists():
        session_file.parent.mkdir(parents=True)

    with session_file.open("w+") as f:
        f.write(token)

    print(f"Session created for organization {organization} and user {username}")

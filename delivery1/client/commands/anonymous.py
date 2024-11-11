import base64
import sys
from hashlib import sha512
from pathlib import Path

import requests
import typer

from utils.consts import ORGANIZATION_URL, SUBJECT_URL
from utils.encryption.encryptors import (
    encrypt_dict_repository,
    decrypt_asymmetric,
    decrypt_symmetric,
)
from utils.encryption.loaders import load_private_key
from utils.repository_info import get_repository_iv
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

    (key, data) = encrypt_dict_repository(obj)

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
    iv = get_repository_iv()
    with private_key_file.open() as f:
        private_key = f.read()

    obj: dict[str, str] = {
        "organization": organization,
        "username": username,
        "password": password,
        "credentials": base64.encodebytes(private_key.encode()).decode(),
    }
    (key, data) = encrypt_dict_repository(obj)

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

    key = decrypt_asymmetric(
        response.headers["Authorization"]
        .replace("\\n", "\n")
        .replace("\\r", "\r")
        .encode(),
        private,
    )
    token = decrypt_symmetric(response.content, key, iv).decode()
    session_file = (
        session_file
        or get_storage_dir()
        / "sessions"
        / organization
        / f".{sha512(username.encode()).hexdigest()}"
    )

    if not session_file.parent.exists():
        session_file.parent.mkdir(parents=True)

    with session_file.open("w+") as f:
        f.write(token)

    print(f"Session created for organization {organization} and user {username}")


@app.command("rep_get_file")
def get_file(file_handle: str, file: Path | None):
    response = requests.get(f"{SUBJECT_URL}/files/{file_handle}")

    if response.status_code == 200:
        file_content = response.content

        if file:
            with file.open("wb") as f:
                f.write(file_content)

            print(f"File saved in {file}")

        else:
            sys.stdout.buffer.write(file_content)
            sys.stdout.flush()

    else:
        print(f"Failure {response.status_code} retriving {response.text}")

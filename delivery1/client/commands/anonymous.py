import base64
import sys
from hashlib import sha512
from pathlib import Path
from typing import Annotated

import requests
import typer

from utils.consts import ORGANIZATION_URL, SUBJECT_URL, DOCUMENT_URL, REPOSITORY_URL
from utils.encryption.loaders import load_private_key
from utils.request import request_repository
from utils.storage import get_storage_dir
from utils.types import RepPublicKey, RepAddress

app = typer.Typer()


@app.command("rep_create_org")
def create_organization(
        organization: str,
        username: str,
        name: str,
        email: str,
        public_key_file: Path,
        repository_public_key: RepPublicKey,
        repository_address: RepAddress,
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

    body, _ = request_repository(
        "POST",
        f"{repository_address}{ORGANIZATION_URL}",
        obj,
        None,
        repository_public_key,
    )

    print(f"Created organization {organization}")


@app.command("rep_list_orgs")
def list_organizations(
        repository_public_key: RepPublicKey,
        repository_address: RepAddress,
):
    response = requests.get(f"{repository_address}{ORGANIZATION_URL}")
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
        repository_public_key: RepPublicKey,
        repository_address: RepAddress,
        session_file: Path | None = None,
):
    with private_key_file.open() as f:
        private_key_str = f.read().encode()
        private_key = load_private_key(private_key_str, password)[0]

    obj: dict[str, str] = {
        "organization": organization,
        "username": username,
        "password": password,
        "credentials": base64.encodebytes(private_key_str).decode(),
    }

    body, _ = request_repository(
        "POST",
        f"{repository_address}{SUBJECT_URL}/session",
        obj,
        private_key,
        repository_public_key,
    )
    token = body.strip('"')

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

    print(
        f"Session created for organization {organization} and user {username} at {session_file}"
    )


# rep_get_file <file handle> [file]
@app.command("rep_get_file")
def get_file(
        file_handle: str,
        repository_address: RepAddress,
        file: Annotated[Path | None, typer.Argument()] = None,
):
    response = requests.get(f"{repository_address}{DOCUMENT_URL}/handle/{file_handle}")

    if response.status_code == 404:
        print("File not found")
        raise typer.Exit(code=-1)

    content = base64.decodebytes(response.content.replace(b"\\n", b"\n").strip(b'"'))

    if file is None:
        sys.stdout.buffer.write(content)
        return

    if not file.parent.exists():
        file.parent.mkdir(parents=True)

    with file.open("wb+") as f:
        f.write(content)
        print(f"File saved as {file}")


@app.command("rep_get_pub_key")
def get_public_key(
        repository_address: RepAddress,
        file: Path,
):
    response = requests.get(f"{repository_address}{REPOSITORY_URL}/public_key")
    body = response.content

    if not file.parent.exists():
        file.parent.mkdir(parents=True)

    with file.open("w+") as f:
        f.write(body.replace(b"\\n", b"\n").strip(b'"').decode())
        print(f"Public key saved as {file}")


@app.command("rep_ping")
def ping(repository_address: RepAddress):
    response = requests.get(f"{repository_address}{REPOSITORY_URL}/ping")

    if response.status_code != 200:
        print("Repository is not available")
        raise typer.Exit(code=-1)

    print("Repository is available")


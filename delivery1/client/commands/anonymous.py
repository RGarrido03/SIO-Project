import base64
import json
import sys
from hashlib import sha512
from pathlib import Path

import requests
import typer

from utils.consts import ORGANIZATION_URL, SUBJECT_URL
from utils.encryption.loaders import load_private_key
from utils.request import request_repository
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

    body, _ = request_repository("POST", ORGANIZATION_URL, obj, None)
    body = json.loads(body)

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
        private_key_str = f.read().encode()
        private_key = load_private_key(private_key_str, password)[0]

    obj: dict[str, str] = {
        "organization": organization,
        "username": username,
        "password": password,
        "credentials": base64.encodebytes(private_key_str).decode(),
    }

    body, _ = request_repository("POST", f"{SUBJECT_URL}/session", obj, private_key)
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

    print(f"Session created for organization {organization} and user {username}")


@app.command("rep_get_file")
def get_file(
    file_handle: str,
    file: Path | None
):
    response = requests.get({file_handle})

    if file:
        with file.open("wb") as f:
            f.write(response)
    
        print(f"File saved in {file}")

        sys.stdout.buffer.write(response)
        sys.stdout.flush()
            

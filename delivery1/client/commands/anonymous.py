from pathlib import Path

import requests
import typer

from utils.consts import ORGANIZATION_URL
from utils.encryption.encryptors import encrypt_dict

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

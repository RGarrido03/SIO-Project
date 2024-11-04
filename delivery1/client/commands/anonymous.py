from pathlib import Path

import requests
import typer

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

    response = requests.post(
        "http://localhost:8000/organization",
        data=encrypt_dict(obj),
        headers={
            "Content-Type": "application/json",
            "Encryption": "repository",
        },
    )
    body = response.json()
    print(f"Created organization {body['name']}")


@app.command("rep_list_orgs")
def list_organizations():
    response = requests.get("http://localhost:8000/organization")
    body = response.json()
    print("Organizations:")
    for org in body:
        print(" - " + org["name"])

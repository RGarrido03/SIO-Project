from pathlib import Path

import requests
import typer

from utils.encryption.encryptors import encrypt_dict

app = typer.Typer()


@app.command()
def rep_create_org(
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


if __name__ == "__main__":
    app()

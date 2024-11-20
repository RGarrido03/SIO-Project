import base64
import json
import os
from hashlib import sha256
from pathlib import Path
from typing import Annotated

import typer

from commands.anonymous import get_file
from commands.local import decrypt_file
from utils.consts import DOCUMENT_URL, SUBJECT_URL
from utils.encryption.encryptors import encrypt_symmetric
from utils.request import request_session
from utils.types import RepPublicKey, RepAddress

app = typer.Typer()


# rep_add_doc <session file> <document name> <file>
@app.command("rep_add_doc")
def add_document(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: Path,
    doc_name: str,
    file: Path,
    # organization_name: str,
    # creator_username: str,
    # alg: str,
    # key: str,
    # acl: dict,
):
    try:
        # checj if existes
        # enc doc with alg and key

        f = open(file, "rb")
        file_readed = f.read()
        # encrypt file
        alg = "AES"  # TODO OVERRIDE THIS IN THE FUTURE
        key = os.urandom(32)
        iv = os.urandom(16)
        enc_file = encrypt_symmetric(file_readed, key, iv)
        file_handle = sha256(enc_file).hexdigest()

        enc_file = enc_file.decode()
        f.close()

        meta = {
            "name": doc_name,
            "file_handle": file_handle,
            "acl": {},
            "organization_name": "",
            "creator_username": "",
            "alg": alg,
            "key": base64.encodebytes(key).decode(),
            "iv": base64.encodebytes(iv).decode(),
            "file_content": enc_file,
        }

        body, _ = request_session(
            "POST",
            f"{repository_address}{DOCUMENT_URL}",
            meta,
            session_file.read_bytes(),
            repository_public_key,
        )

        body = json.loads(body)
        print(body)

    except Exception as e:
        print(e)


# rep_get_doc_metadata <session file> <document name>
@app.command("rep_get_doc_metadata")
def get_document_metadata(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: Path,
    doc_name: str,
) -> tuple[str, Path, str]:
    try:

        body, _ = request_session(
            "GET",
            f"{repository_address}{DOCUMENT_URL}/{doc_name}",
            None,
            session_file.read_bytes(),
            repository_public_key,
        )
        body = json.loads(body)

        # store this in a file
        path = f"storage/docs/{body['organization_name']}"
        if not os.path.exists(path):
            os.makedirs(path)

        f = open(f"{path}/{doc_name}.json", "w+")
        f.write(json.dumps(body))
        f.close()

        print(body)
        return (
            body["file_handle"],
            Path(f"{path}/{doc_name}.json"),
            body["organization_name"],
        )
    except Exception as e:
        print(e)


# rep_get_doc_file <session file> <document name> [file]
@app.command("rep_get_doc_file")
def get_document_file(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: Path,
    doc_name: str,
    file: Annotated[Path | None, typer.Argument()] = None,
):
    try:
        file_handle, enc_meta_file_path, organization = get_document_metadata(
            repository_public_key, repository_address, session_file, doc_name
        )

        enc_file_path = Path(f"storage/docs/{organization}/{file_handle}")

        get_file(file_handle, repository_address, enc_file_path)

        dec_file = decrypt_file(enc_file_path, enc_meta_file_path)
        if file:
            with file.open("wb+") as f:
                f.write(dec_file)
                print(f"File saved at {file}")
            return

        print(dec_file.decode())

    except Exception as e:
        print(e)


# rep_delete_doc <session file> <document name>
@app.command("rep_delete_doc")
def delete_document(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: Path,
    doc_name: str,
):
    try:
        body, _ = request_session(
            "DELETE",
            f"{repository_address}{DOCUMENT_URL}/{doc_name}",
            None,
            session_file.read_bytes(),
            repository_public_key,
        )
        print(body.strip('"'))
    except Exception as e:
        print(e)


# rep_add_subject <session file> <username> <name> <email> <credentials file>


@app.command("rep_add_subject")
def add_subject(
    session_file: Path,
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
        "username": username,
        "full_name": name,
        "email": email,
        "public_key": public_key,
    }

    body, _ = request_session(
        "POST",
        f"{repository_address}{SUBJECT_URL}",
        obj,
        session_file.read_bytes(),
        repository_public_key,
    )
    body = json.loads(body)

    print(f"{body}")

    # print(f"Created organization {body['name']}")


# rep_suspend_subject <session file> <username>
@app.command("rep_suspend_subject")
def suspend_subject(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: Path,
    username: str,
):
    params = {"username": username, "active": False}
    body, _ = request_session(
        "PATCH",
        f"{repository_address}{SUBJECT_URL}/activation",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params=params,
    )
    body = json.loads(body)
    print(body)


# rep_activate_subject <session file> <username>
@app.command("rep_activate_subject")
def activate_subject(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: Path,
    username: str,
):
    params = {"username": username, "active": True}
    body, _ = request_session(
        "PATCH",
        f"{repository_address}{SUBJECT_URL}/activation",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params=params,
    )
    body = json.loads(body)
    print(body)

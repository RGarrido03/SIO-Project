import base64
import json
import os
from hashlib import sha256
from pathlib import Path
from typing import Annotated

import click
import typer

from commands.anonymous import get_file
from commands.local import decrypt_file
from utils.consts import DOCUMENT_URL, SUBJECT_URL, ROLE_URL
from utils.encryption.encryptors import encrypt_symmetric
from utils.output import (
    print_subject,
    print_doc_metadata,
    print_organization_role,
    print_roles_list,
)
from utils.permission import DocumentPermission, Permission
from utils.request import request_with_session
from utils.types import RepPublicKey, RepAddress, PathWithCheck, PermissionOrStr

app = typer.Typer()


# rep_add_doc <session file> <document name> <file>
@app.command("rep_add_doc")
def add_document(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    doc_name: str,
    file: Path,
):
    # check if existes
    # enc doc with alg and key

    f = open(file, "rb")
    file_readed = f.read()

    # encrypt file
    alg = "AES"  # TODO OVERRIDE THIS IN THE FUTURE
    key = os.urandom(32)
    iv = os.urandom(16)
    enc_file = encrypt_symmetric(file_readed, key, iv)
    enc_file = base64.encodebytes(enc_file)
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

    body, _ = request_with_session(
        "POST",
        repository_address,
        f"{DOCUMENT_URL}",
        meta,
        session_file.read_bytes(),
        repository_public_key,
    )

    body = json.loads(body)
    print_doc_metadata(body, include_encryption=True)


# rep_get_doc_metadata <session file> <document name>
@app.command("rep_get_doc_metadata")
def get_document_metadata(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    doc_name: str,
) -> tuple[str, Path, str]:
    body, _ = request_with_session(
        "GET",
        repository_address,
        f"{DOCUMENT_URL}/{doc_name}",
        None,
        session_file.read_bytes(),
        repository_public_key,
    )
    body = json.loads(body)

    path = f"storage/docs/{body['organization_name']}"
    if not os.path.exists(path):
        os.makedirs(path)

    f = open(f"{path}/{doc_name}.json", "w+")
    f.write(json.dumps(body))
    f.close()

    print_doc_metadata(body, include_encryption=True)

    return (
        body["file_handle"],
        Path(f"{path}/{doc_name}.json"),
        body["organization_name"],
    )


# rep_get_doc_file <session file> <document name> [file]
@app.command("rep_get_doc_file")
def get_document_file(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    doc_name: str,
    file: Annotated[Path | None, typer.Argument()] = None,
):
    file_handle, enc_meta_file_path, organization = get_document_metadata(
        repository_public_key, repository_address, session_file, doc_name
    )

    enc_file_path = Path(f"storage/docs/{organization}/{file_handle}")

    get_file(file_handle, repository_public_key, repository_address, enc_file_path)
    dec_file = decrypt_file(enc_file_path, enc_meta_file_path)

    if file:
        with file.open("wb+") as f:
            f.write(dec_file)
            print(f"File saved at {file}")
        return

    print(dec_file.decode())


# rep_delete_doc <session file> <document name>
@app.command("rep_delete_doc")
def delete_document(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    doc_name: str,
):
    body, _ = request_with_session(
        "DELETE",
        repository_address,
        f"{DOCUMENT_URL}/{doc_name}",
        None,
        session_file.read_bytes(),
        repository_public_key,
    )
    print_doc_metadata(json.loads(body), include_encryption=True)


# rep_add_subject <session file> <username> <name> <email> <credentials file>
@app.command("rep_add_subject")
def add_subject(
    session_file: PathWithCheck,
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

    body, _ = request_with_session(
        "POST",
        repository_address,
        f"{SUBJECT_URL}",
        obj,
        session_file.read_bytes(),
        repository_public_key,
    )
    body = json.loads(body)
    print_subject(body, include_email=True)


# rep_suspend_subject <session file> <username>
@app.command("rep_suspend_subject")
def suspend_subject(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    username: str,
):
    params = {"username": username}
    body, _ = request_with_session(
        "PATCH",
        repository_address,
        f"{SUBJECT_URL}/activation/suspend",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params=params,
    )
    body = json.loads(body)
    print_subject(body)


# rep_activate_subject <session file> <username>
@app.command("rep_activate_subject")
def activate_subject(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    username: str,
):
    params = {"username": username}
    body, _ = request_with_session(
        "PATCH",
        repository_address,
        f"{SUBJECT_URL}/activation/activate",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params=params,
    )
    body = json.loads(body)
    print_subject(body)


"""Second delivery"""


# rep_add_role <session file> <role>
@app.command("rep_add_role")
def add_role(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    role: str,
):
    body, _ = request_with_session(
        "POST",
        repository_address,
        f"{ROLE_URL}",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params={"role": role},
    )

    body = json.loads(body)
    print(f"Added role {role} to {body["organization_name"]}")
    print_organization_role(body)


# rep_suspend_role <session file> <role>
@app.command("rep_suspend_role")
def suspend_role(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    role: str,
):
    body, _ = request_with_session(
        "PATCH",
        repository_address,
        f"{ROLE_URL}/activation/suspend",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params={"role": role},
    )

    body = json.loads(body)
    print(f"Role {role} suspended in {body["organization_name"]}")
    print_organization_role(body)


# rep_reactivate_role <session file> <role>
@app.command("rep_reactivate_role")
def reactivate_role(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    role: str,
):
    body, _ = request_with_session(
        "PATCH",
        repository_address,
        f"{ROLE_URL}/activation/activate",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params={"role": role},
    )

    body = json.loads(body)
    print(f"Role {role} activated in {body["organization_name"]}")
    print_organization_role(body)


def manage_permission(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    role: str,
    username_or_permission: PermissionOrStr,
    add: bool,
):
    url = (
        f"{ROLE_URL}/permission"
        if isinstance(username_or_permission, Permission)
        else f"{SUBJECT_URL}/role"
    )
    params = {
        "role": role,
        (
            "permission"
            if isinstance(username_or_permission, Permission)
            else "username"
        ): username_or_permission,
    }

    body, _ = request_with_session(
        "POST" if add else "DELETE",
        repository_address,
        url,
        None,
        session_file.read_bytes(),
        repository_public_key,
        params=params,
    )
    body = json.loads(body)

    if isinstance(username_or_permission, Permission):
        print_organization_role(body)
        return

    print_roles_list(body)


# rep_add_permission <session file> <role> <username | permission>
@app.command("rep_add_permission")
def add_username_permission(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    role: str,
    username_or_permission: PermissionOrStr,
):
    return manage_permission(
        repository_public_key,
        repository_address,
        session_file,
        role,
        username_or_permission,
        True,
    )


# rep_remove_permission <session file> <role> <username | permission>
@app.command("rep_remove_permission")
def remove_username_permission(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    role: str,
    username_or_permission: PermissionOrStr,
):
    return manage_permission(
        repository_public_key,
        repository_address,
        session_file,
        role,
        username_or_permission,
        False,
    )


# rep_acl_doc <session file> <document name> [+/-] <role> <permission>
@app.command("rep_acl_doc")
def change_acl_permissions(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    doc_name: str,
    choice: Annotated[str, typer.Argument(click_type=click.Choice(["+", "-"]))],
    role: str,
    permission: Annotated[DocumentPermission, typer.Argument(case_sensitive=False)],
):
    body, _ = request_with_session(
        "PATCH",
        repository_address,
        f"{DOCUMENT_URL}/{doc_name}/acl",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params={
            "role": role,
            "add": choice == "+",
            "permission": permission.name,
        },
    )

    body = json.loads(body)
    print_doc_metadata(body)

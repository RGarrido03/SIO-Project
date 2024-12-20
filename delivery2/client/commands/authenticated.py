import json
from typing import Annotated

import typer

from utils.consts import DOCUMENT_URL, SUBJECT_URL, ROLE_URL
from utils.output import (
    print_roles_list,
    print_permissions_list,
    print_doc_metadata,
    print_subject,
)
from utils.permission import Permission
from utils.request import request_with_session
from utils.types import RepPublicKey, RepAddress, PathWithCheck

app = typer.Typer()


# rep_list_subjects <session file> [username]
@app.command("rep_list_subjects")
def list_subjects(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    username: Annotated[str | None, typer.Argument()] = None,
):
    params = {"username": username}

    body, _ = request_with_session(
        "GET",
        repository_address,
        f"{SUBJECT_URL}",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params=params,
    )
    body = json.loads(body)
    print_subject(body, many=True)


@app.command("rep_list_docs")
def list_documents(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    username: Annotated[
        str | None,
        typer.Option("-s", "--username", help="Filter by username"),
    ] = None,
    date: Annotated[
        tuple[str, str] | None,
        typer.Option("-d", "--date", help="Filter by date"),
    ] = None,
):
    if date is not None and date[0] not in ["nt", "ot", "et"]:
        raise typer.BadParameter(
            "Invalid date filter. Must be one of 'nt', 'ot', 'et'."
        )

    params = {
        "username": username,
        "date": date[1] if date is not None else None,
        "date_order": date[0] if date is not None else None,
    }

    body, _ = request_with_session(
        "GET",
        repository_address,
        f"{DOCUMENT_URL}",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params=params,
    )
    body = json.loads(body)
    for doc in body:
        print_doc_metadata(doc)
        print(f"\n{'-'*64}\n")


"""Second delivery"""


# rep_assume_role <session file> <role>
@app.command("rep_assume_role")
def assume_role(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    role: str,
):
    body, _ = request_with_session(
        "POST",
        repository_address,
        f"{SUBJECT_URL}/session/role",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params={"role": role},
    )

    token = body.strip('"')
    with session_file.open("w") as f:
        f.write(token)

    print(f"Added role {role} to session file {session_file}.")


# rep_drop_role <session file> <role>
@app.command("rep_drop_role")
def drop_role(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    role: str,
):
    body, _ = request_with_session(
        "DELETE",
        repository_address,
        f"{SUBJECT_URL}/session/role",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params={"role": role},
    )

    token = body.strip('"')
    with session_file.open("w") as f:
        f.write(token)

    print(f"Removed role {role} to session file {session_file}.")


# rep_list_roles <session file>
@app.command("rep_list_roles")
def list_roles(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
):
    body, _ = request_with_session(
        "GET",
        repository_address,
        f"{SUBJECT_URL}/session/role",
        None,
        session_file.read_bytes(),
        repository_public_key,
    )

    body = json.loads(body)
    print_roles_list(body)


# rep_list_role_subjects <session file> <role>
@app.command("rep_list_role_subjects")
def list_role_subjects(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    role: str,
):
    body, _ = request_with_session(
        "GET",
        repository_address,
        f"{ROLE_URL}/subject",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params={"role": role},
    )

    body = json.loads(body)
    print_subject(body, many=True)


# rep_list_subject_roles <session file> <username>
@app.command("rep_list_subject_roles")
def assume_role(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    username: str,
):
    body, _ = request_with_session(
        "GET",
        repository_address,
        f"{SUBJECT_URL}/role",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params={"subject": username},
    )

    body = json.loads(body)
    print_roles_list(body)


# rep_list_role_permissions <session file> <role>
@app.command("rep_list_role_permissions")
def list_role_permissions(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    role: str,
):
    body, _ = request_with_session(
        "GET",
        repository_address,
        f"{ROLE_URL}/permission",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params={"role": role},
    )

    body = json.loads(body)
    print_permissions_list(body)


# rep_list_permission_roles <session file> <permission>
@app.command("rep_list_permission_roles")
def list_permission_roles(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    permission: Annotated[Permission, typer.Argument(case_sensitive=False)],
):
    body, _ = request_with_session(
        "GET",
        repository_address,
        f"{ROLE_URL}",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params={"permission": permission.name},
    )

    body = json.loads(body)
    print_roles_list(body)

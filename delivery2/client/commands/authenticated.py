import json
from typing import Annotated

import typer
from tabulate import tabulate

from utils.consts import DOCUMENT_URL, SUBJECT_URL, ROLE_URL
from utils.permission import Permission
from utils.request import request_session
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

    body, _ = request_session(
        "GET",
        f"{repository_address}{SUBJECT_URL}",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params=params,
    )
    body = json.loads(body)

    headers = {
        "username": "Username",
        "full_name": "Name",
        "active": "Active",
    }
    body = [{key: doc.get(key) for key in headers.keys()} for doc in body]

    print(
        tabulate(
            body,
            headers=headers,
            tablefmt="rounded_outline",
        )
    )


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

    body, _ = request_session(
        "GET",
        f"{repository_address}{DOCUMENT_URL}",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params=params,
    )
    body = json.loads(body)

    headers = {
        "file_handle": "File handle",
        "name": "Name",
        "organization_name": "Organization",
        "creator_username": "Creator",
        "deleter_username": "Deleter",
        "acl": "ACL",
    }
    body = [{key: doc.get(key) for key in headers.keys()} for doc in body]

    print(
        tabulate(
            body,
            headers=headers,
            tablefmt="rounded_outline",
        )
    )


"""Second delivery"""


# rep_assume_role <session file> <role>
@app.command("rep_assume_role")
def assume_role(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    role: str,
):
    body, _ = request_session(
        "POST",
        f"{repository_address}{SUBJECT_URL}/session/role",
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
    body, _ = request_session(
        "DELETE",
        f"{repository_address}{SUBJECT_URL}/session/role",
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
    body, _ = request_session(
        "GET",
        f"{repository_address}{SUBJECT_URL}/session/role",
        None,
        session_file.read_bytes(),
        repository_public_key,
    )

    body = json.loads(body)

    print(
        tabulate(
            [[role] for role in body] if len(body) > 0 else [["No roles assigned."]],
            headers=["Roles"],
            tablefmt="rounded_outline",
        )
    )


# rep_list_role_subjects <session file> <role>
@app.command("rep_list_role_subjects")
def list_role_subjects(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    role: str,
):
    body, _ = request_session(
        "GET",
        f"{repository_address}{ROLE_URL}/subject",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params={"role": role},
    )

    body = json.loads(body)

    headers = {
        "username": "Username",
        "full_name": "Name",
        "active": "Active",
    }
    body = [{key: doc.get(key) for key in headers.keys()} for doc in body]

    print(
        tabulate(
            body,
            headers=headers,
            tablefmt="rounded_outline",
        )
    )


# rep_list_subject_roles <session file> <username>
@app.command("rep_list_subject_roles")
def assume_role(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    username: str,
):
    body, _ = request_session(
        "GET",
        f"{repository_address}{SUBJECT_URL}/role",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params={"subject": username},
    )

    body = json.loads(body)
    print(
        tabulate(
            [[role] for role in body] if len(body) > 0 else [["No roles assigned."]],
            headers=["Roles"],
            tablefmt="rounded_outline",
        )
    )


# rep_list_role_permissions <session file> <role>
@app.command("rep_list_role_permissions")
def list_role_permissions(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    role: str,
):
    body, _ = request_session(
        "GET",
        f"{repository_address}{ROLE_URL}/permission",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params={"role": role},
    )

    body = json.loads(body)
    print(
        tabulate(
            (
                [[permission] for permission in body]
                if len(body) > 0
                else [["No permissions assigned."]]
            ),
            headers=["Permissions"],
            tablefmt="rounded_outline",
        )
    )


# rep_list_permission_roles <session file> <permission>
@app.command("rep_list_permission_roles")
def list_permission_roles(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: PathWithCheck,
    permission: Annotated[Permission, typer.Argument(case_sensitive=False)],
):
    body, _ = request_session(
        "GET",
        f"{repository_address}{ROLE_URL}",
        None,
        session_file.read_bytes(),
        repository_public_key,
        params={"permission": permission.name},
    )

    body = json.loads(body)
    print(
        tabulate(
            ([[role] for role in body] if len(body) > 0 else [["No roles assigned."]]),
            headers=["Roles"],
            tablefmt="rounded_outline",
        )
    )

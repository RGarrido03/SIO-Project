import json
from typing import Annotated

import typer
from tabulate import tabulate

from utils.consts import DOCUMENT_URL, SUBJECT_URL
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

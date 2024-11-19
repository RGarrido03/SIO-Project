import json
from pathlib import Path
from typing import Annotated

import typer

from utils.consts import DOCUMENT_URL, SUBJECT_URL
from utils.request import request_session
from utils.types import RepPublicKey, RepAddress

app = typer.Typer()

@app.command("rep_list_subjects")
def list_subjects(
    session_file: Path,
    username: str | None = None
):
    params = {
        "username": username,
        "active": bool
    }

    body, _ = request_session(
        "GET", SUBJECT_URL, None, session_file.read_bytes(), params=params
    )
    body = json.loads(body)
    print(body)


@app.command("rep_list_docs")
def list_documents(
    repository_public_key: RepPublicKey,
    repository_address: RepAddress,
    session_file: Path,
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
    print(body)

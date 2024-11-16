from pathlib import Path
from typing import Annotated

import requests
import typer

from utils.consts import DOCUMENT_URL
from utils.encryption.encryptors import encrypt_key

app = typer.Typer()


@app.command("rep_list_docs")
def list_documents(
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

    key = encrypt_key(session_file.read_bytes())

    params = {
        "username": username,
        "date": date[1] if date is not None else None,
        "date_order": date[0] if date is not None else None,
    }

    response = requests.get(
        DOCUMENT_URL,
        params=params,
        headers={
            "Encryption": "session",
            "Authorization": key,
        },
    )
    body = response.json()
    print(body)

import json
from pathlib import Path
from typing import Annotated

import typer

from utils.consts import DOCUMENT_URL
from utils.request import request_session

app = typer.Typer()


# rep_add_doc <session file> <document name> <file>
@app.command("rep_add_doc")
def add_document(
    session_file: Path,
    name: str,
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
        #handle sha256 digest of file
        b = {
            "name": name,
            "file_handle": file_handle,
            "organization_name": organization_name,
            "creator_username": creator_username,
            "alg": alg, # generated
            "key": key, # generated
            "acl": {},
        }

        body, _ = request_session(
            "POST", DOCUMENT_URL, b, session_file.read_bytes()
        )




    except Exception as e:
        print(e)

import base64
import json
import os
from pathlib import Path
from pprint import pprint
from typing import Annotated
from hashlib import sha256
import typer

from utils.consts import DOCUMENT_URL
from utils.encryption.encryptors import encrypt_key, encrypt_symmetric
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
        enc_file = encrypt_symmetric(file_readed, key, iv).decode()
        file_handle = sha256(enc_file.encode()).hexdigest()
        f.close()


        meta = {
            "name": doc_name,
            "file_handle": file_handle,
            "acl": {},
            "organization_name": "",
            "creator_username": "",
            "alg": alg,
            "key": base64.encodebytes(key).decode(),
            "iv": base64.encodebytes(iv).decode() ,
            "file_content": enc_file
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

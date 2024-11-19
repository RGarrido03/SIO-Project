import re
from pathlib import Path
from typing import Annotated

import click
import typer
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from utils.encryption.loaders import load_public_key


class PublicKeyParser(click.ParamType):
    name = "PUBLIC KEY"

    def convert(self, value, param, ctx):
        p = Path(value)
        if not p.exists():
            print("Given public key path does not exist")
            raise typer.Exit(code=1)
        if p.is_dir():
            print("Given public key path is a directory")
            raise typer.Exit(code=1)
        return load_public_key(p.read_text())


def _validate_address(value: str) -> str:
    if not re.match(r"^([a-zA-Z][a-zA-Z0-9.-]*|\d{1,3}(\.\d{1,3}){3}):(\d+)$", value):
        print("Invalid address format (expected IP:port or domain:port)")
        raise typer.Exit(code=1)
    return "http://" + value


RepPublicKey = Annotated[
    RSAPublicKey,
    typer.Option(
        "-k",
        "--public-key",
        envvar="REP_PUB_KEY",
        help="Repository's public key file path",
        click_type=PublicKeyParser(),
    ),
]


RepAddress = Annotated[
    str,
    typer.Option(
        "-r",
        "--address",
        envvar="REP_ADDRESS",
        help="Repository address (IP:port or domain:port)",
        callback=_validate_address,
    ),
]

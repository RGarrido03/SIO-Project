from typing import Any

from tabulate import tabulate


def print_subject(body: dict[str, Any]) -> None:
    headers = {
        "username": "Username",
        "full_name": "Name",
        "email": "E-mail",
        "active": "Active",
    }
    body_mod = [{key: body.get(key) for key in headers.keys()}]

    print(
        tabulate(
            body_mod,
            headers=headers,
            tablefmt="rounded_outline",
        )
    )


def print_doc_metadata(body: dict[str, Any]) -> None:
    headers_info = {
        "file_handle": "File handle",
        "name": "Name",
        "organization_name": "Organization",
        "creator_username": "Creator",
        "deleter_username": "Deleter",
        "acl": "ACL",
    }

    headers_enc = {
        "alg": "Algorithm",
        "key": "Key (base64)",
        "iv": "IV (base64)",
    }

    body_info = [{key: body.get(key) for key in headers_info.keys()}]
    body_enc = [{key: body.get(key) for key in headers_enc.keys()}]

    print(
        tabulate(
            body_info,
            headers=headers_info,
            tablefmt="rounded_outline",
        )
    )

    print(
        tabulate(
            body_enc,
            headers=headers_enc,
            tablefmt="rounded_outline",
        )
    )

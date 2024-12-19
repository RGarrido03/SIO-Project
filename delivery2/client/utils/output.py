from typing import Any

from tabulate import tabulate


def print_subject(body: dict[str, Any], include_email: bool = False) -> None:
    headers = {
        "username": "Username",
        "full_name": "Name",
        "active": "Active",
    }

    if include_email:
        headers["email"] = "E-mail"

    body_mod = [{key: body.get(key) for key in headers.keys()}]

    print(
        tabulate(
            body_mod,
            headers=headers,
            tablefmt="rounded_outline",
        )
    )


def print_doc_metadata(body: dict[str, Any], include_encryption: bool = False) -> None:
    headers_info = {
        "file_handle": "File handle",
        "name": "Name",
        "organization_name": "Organization",
        "creator_username": "Creator",
        "deleter_username": "Deleter",
        "acl": "ACL",
    }

    body_info = [{key: body.get(key) for key in headers_info.keys()}]
    print(
        tabulate(
            body_info,
            headers=headers_info,
            tablefmt="rounded_outline",
        )
    )

    if not include_encryption:
        return

    headers_enc = {
        "alg": "Algorithm",
        "key": "Key (base64)",
        "iv": "IV (base64)",
    }

    body_enc = [{key: body.get(key) for key in headers_enc.keys()}]

    print(
        tabulate(
            body_enc,
            headers=headers_enc,
            tablefmt="rounded_outline",
        )
    )


def print_organization_role(body: dict[str, Any]) -> None:
    headers = {
        "organization_name": "Organization",
        "role": "Role",
        "active": "Active",
        "permissions": "Permissions",
    }

    body = [{key: body.get(key) for key in headers.keys()}]
    print(tabulate(body, headers=headers, tablefmt="rounded_outline"))


def _print_list(body: list[Any], header: str, default: str = "Not found") -> None:
    print(
        tabulate(
            [[element] for element in body] if len(body) > 0 else [[default]],
            headers=[header],
            tablefmt="rounded_outline",
        )
    )


def print_roles_list(body: list[str]):
    _print_list(body, "Roles", "No roles assigned.")


def print_permissions_list(body: list[str]):
    _print_list(body, "Permissions", "No permissions assigned.")


def print_organizations_list(body: list[str]):
    _print_list(body, "Organizations", "No organizations available.")

from datetime import datetime
from typing import cast

from cryptography.hazmat.primitives._serialization import Encoding, PublicFormat

from repository.config.database import get_session
from repository.crud.base import CRUDBase
from repository.models.permission import RoleEnum
from repository.models.relations import (
    SubjectOrganizationLink,
    SubjectOrganizationLinkCreate,
)
from repository.models.session import Session, SessionWithSubjectInfo
from repository.utils.auth.generate_token import AuthSessionLogin, create_token
from repository.utils.encryption.encryptors import encrypt_asymmetric
from repository.utils.encryption.loaders import load_private_key


class CRUDSubjectOrganizationLink(
    CRUDBase[SubjectOrganizationLink, SubjectOrganizationLinkCreate, tuple[str, str]]
):
    def __init__(self) -> None:
        super().__init__(SubjectOrganizationLink)

    async def create_session(self, info: AuthSessionLogin) -> bytes:
        async with get_session() as session:
            rel = await self.get((info.username, info.organization), session)
            if rel is None:
                raise ValueError("Subject not found")

            (private_key, public_key) = load_private_key(
                await info.credentials.read(), info.password
            )

            if public_key.public_bytes(
                Encoding.PEM, PublicFormat.PKCS1
            ).decode() not in [pk.key for pk in rel.subject.public_keys]:
                raise ValueError("Public key not found in user keys")

        rel.session = Session(  # TODO: Generate key
            keys=["lorem", "ipsum"],
        )

        rel = await self.update(
            (info.username, info.organization),
            rel,  # type: ignore
        )

        # Not null checks, however, this will never be None
        # I'm doing this because otherwise PyCharm yells at me
        rel = cast(SubjectOrganizationLink, rel)
        if rel.session is None:
            raise ValueError("Session not created")

        token = create_token(
            SessionWithSubjectInfo(
                **rel.session.model_dump(),
                username=info.username,
                organization=info.organization
            )
        )

        return encrypt_asymmetric(token.encode(), public_key)

    async def get_and_verify_session(
        self, username: str, organization: str
    ) -> SubjectOrganizationLink:
        result = await self.get((username, organization))
        if result is None:
            raise ValueError("Subject not found")
        # TODO: These changes should come from the session validators (some auth middleware)
        if not result.subject.active:
            raise ValueError("Subject is not active")
        if result.session is None:
            raise ValueError("Session not found")
        if result.session.expires < datetime.now():
            raise ValueError("Session expired")
        return result

    async def manage_role_in_session(
        self, obj: SubjectOrganizationLink, role: RoleEnum, add: bool
    ) -> SessionWithSubjectInfo:
        if obj.session is None:
            raise ValueError("Session not found")

        if add:
            obj.session.roles.add(role)
        else:
            obj.session.roles.remove(role)

        obj = await self._add_to_db(obj)
        return SessionWithSubjectInfo(
            **obj.session.model_dump() if obj.session is not None else {},
            username=obj.subject_username,
            organization=obj.organization_name
        )

    async def add_role_to_session(
        self, obj: SubjectOrganizationLink, role: RoleEnum
    ) -> SessionWithSubjectInfo:
        return await self.manage_role_in_session(obj, role, True)

    async def drop_role_from_session(
        self, obj: SubjectOrganizationLink, role: RoleEnum
    ) -> SessionWithSubjectInfo:
        return await self.manage_role_in_session(obj, role, False)


crud_subject_organization_link = CRUDSubjectOrganizationLink()

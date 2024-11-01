from datetime import datetime

from cryptography.hazmat.primitives._serialization import Encoding, PublicFormat

from repository.config.database import get_session
from repository.crud.base import CRUDBase
from repository.models.permission import RoleEnum
from repository.models.relations import (
    SubjectOrganizationLink,
    SubjectOrganizationLinkCreate,
)
from repository.models.session import Session, SessionCreate, SessionWithSubjectInfo
from repository.utils.encryption import load_private_key


class CRUDSubjectOrganizationLink(
    CRUDBase[SubjectOrganizationLink, SubjectOrganizationLinkCreate, tuple[str, str]]
):
    def __init__(self) -> None:
        super().__init__(SubjectOrganizationLink)

    async def create_session(self, info: SessionCreate) -> SessionWithSubjectInfo:
        async with get_session() as session:
            rel = await self.get((info.username, info.organization), session)
            if rel is None:
                raise ValueError("Subject not found")

            if info.public not in [pk.key for pk in rel.subject.public_keys]:
                raise ValueError("Public key not found in user keys")

        decrypted_private = load_private_key(info.private, info.password)
        if (
            decrypted_private.public_key().public_bytes(
                Encoding.PEM, PublicFormat.PKCS1
            )
            != rel.publickey.key.encode()
        ):
            raise ValueError("Public key in the database does not match private key")

        rel.session = Session(keys=[info.private, info.public])
        await self.update(
            (info.organization, info.username),
            SubjectOrganizationLinkCreate.model_validate(rel),
        )
        return SessionWithSubjectInfo(
            **rel.session.model_dump(),
            username=info.username,
            organization=info.organization
        )

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

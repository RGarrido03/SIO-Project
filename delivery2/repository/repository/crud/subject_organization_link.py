import base64
from typing import cast

from cryptography.hazmat.primitives._serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from sqlmodel import select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from repository.config.database import get_session
from repository.crud.base import CRUDBase
from repository.models.permission import RoleEnum
from repository.models.relations import (
    SubjectOrganizationLink,
    SubjectOrganizationLinkCreate,
)
from repository.models.session import Session, SessionWithSubjectInfo, SessionCreate
from repository.models.subject import SubjectActiveListing
from repository.utils.auth.generate_token import create_token
from repository.utils.encryption.loaders import load_private_key


class CRUDSubjectOrganizationLink(
    CRUDBase[SubjectOrganizationLink, SubjectOrganizationLinkCreate, tuple[str, str]]
):
    def __init__(self) -> None:
        super().__init__(SubjectOrganizationLink)

    async def create_session(self, info: SessionCreate) -> tuple[str, RSAPublicKey]:
        credentials_bytes = base64.decodebytes(info.credentials.encode())
        async with get_session() as session:
            rel = await self.get((info.username, info.organization), session)
            if rel is None:
                raise ValueError("Subject not found")

            (private_key, public_key) = load_private_key(
                credentials_bytes, info.password
            )

            if public_key.public_bytes(
                Encoding.PEM, PublicFormat.PKCS1
            ).decode() not in [pk.key for pk in rel.subject.public_keys]:
                raise ValueError("Public key not found in user keys")

        rel.session = Session(keys=[])
        rel.session.keys = ["".join(str(rel.session.id).split("-"))]

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

        return token, public_key

    async def get_subjects_by_organization(
        self, organization: str, username: str | None
    ) -> list[SubjectActiveListing]:
        async with get_session() as session:
            query: SelectOfScalar[SubjectOrganizationLink] = select(
                SubjectOrganizationLink
            ).where(SubjectOrganizationLink.organization_name == organization)

            if username is not None:
                query = query.where(
                    SubjectOrganizationLink.subject_username == username
                )

            result = await session.exec(query)
            links: list[SubjectOrganizationLink] = list(result.all())
            return [SubjectActiveListing.model_validate(a.subject) for a in links]

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

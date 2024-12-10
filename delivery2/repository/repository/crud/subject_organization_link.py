import base64
from typing import cast

from cryptography.hazmat.primitives._serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from sqlmodel import select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from repository.config.database import get_session
from repository.crud.base import CRUDBase
from repository.crud.organization_role import crud_organization_role
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
                organization=info.organization,
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
            return [
                SubjectActiveListing(**a.subject.model_dump(), active=a.active)
                for a in links
            ]

    async def set_active(
        self, username: str, organization: str, active: bool
    ) -> SubjectOrganizationLink | None:
        link = await self.get((username, organization))
        if link is None:
            return None

        link.active = active
        return await self._add_to_db(link)

    async def manage_role_in_session(
        self, obj: SubjectOrganizationLink, role: str, add: bool
    ) -> str:
        if obj.session is None:
            raise ValueError("Session not found")

        if add:
            if not any(a == role for a in obj.role_ids):
                raise ValueError("Role not found in subject")
            obj.session.roles.add(role)
        else:
            obj.session.roles.remove(role)

        obj = await self._add_to_db(obj)

        token = create_token(
            SessionWithSubjectInfo(
                **obj.session.model_dump(),
                username=obj.subject_username,
                organization=obj.organization_name,
            )
        )
        return token

    async def add_role_to_session(self, obj: SubjectOrganizationLink, role: str) -> str:
        return await self.manage_role_in_session(obj, role, True)

    async def drop_role_from_session(
        self, obj: SubjectOrganizationLink, role: str
    ) -> str:
        return await self.manage_role_in_session(obj, role, False)

    async def manage_subject_role(
        self, organization: str, username: str, role: str, action: str
    ) -> SubjectOrganizationLink:
        role_link = await crud_organization_role.get((organization, role))
        if role_link is None:
            raise ValueError("Role not found")

        link = await self.get((username, organization))
        if link is None:
            raise ValueError("Subject not found")

        r_set = set(link.role_ids)

        match action:
            case "add":
                r_set.add(role)
            case "remove":
                # TODO: The Managers role must have at any time an active subject
                r_set.discard(role)

        link.role_ids = r_set
        return await self._add_to_db(link)

    async def get_subjects_by_role(
        self, organization: str, role: str
    ) -> list[SubjectActiveListing]:
        role_obj = await crud_organization_role.get((organization, role))
        if role_obj is None:
            raise ValueError("Role not found")

        async with get_session() as session:
            result = await session.exec(
                select(SubjectOrganizationLink)
                .where(SubjectOrganizationLink.organization_name == organization)
                .where(SubjectOrganizationLink.role_ids.contains({role}))
            )
            links: list[SubjectOrganizationLink] = list(result.all())
            return [
                SubjectActiveListing(**a.subject.model_dump(), active=a.active)
                for a in links
            ]

    async def get_subject_roles(self, organization: str, subject: str) -> list[str]:
        link = await self.get((subject, organization))
        if link is None:
            raise ValueError("Subject not found")
        return list(link.role_ids)


crud_subject_organization_link = CRUDSubjectOrganizationLink()

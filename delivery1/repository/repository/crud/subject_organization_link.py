from cryptography.hazmat.primitives._serialization import Encoding, PublicFormat

from repository.crud.base import CRUDBase
from repository.models.relations import (
    SubjectOrganizationLink,
    SubjectOrganizationLinkCreate,
)
from repository.models.session import Session, SessionCreate
from repository.utils.encryption import load_private_key


class CRUDSubjectOrganizationLink(
    CRUDBase[SubjectOrganizationLink, SubjectOrganizationLinkCreate, tuple[str, str]]
):
    def __init__(self) -> None:
        super().__init__(SubjectOrganizationLink)

    async def create_session(self, info: SessionCreate) -> Session:
        rel = await self.get((info.organization, info.username))
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
        return rel.session


crud_subject_organization_link = CRUDSubjectOrganizationLink()

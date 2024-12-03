import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, ARRAY, String
from sqlmodel import SQLModel, Field, Relationship

from repository.models.session import Session

if TYPE_CHECKING:
    from repository.models.organization import Organization
    from repository.models.subject import PublicKey
    from repository.models.subject import Subject


class SubjectOrganizationLinkBase(SQLModel):
    subject_username: str = Field(foreign_key="subject.username", primary_key=True)
    organization_name: str = Field(foreign_key="organization.name", primary_key=True)
    public_key_id: uuid.UUID = Field(foreign_key="publickey.id")
    role_ids: list[str] = Field(default=[], sa_column=Column(ARRAY(String)))


class SubjectOrganizationLink(SubjectOrganizationLinkBase, table=True):
    session: Session | None = Field(
        default=None,
        sa_column=Column(Session.to_sa_type(), nullable=True),
    )

    # Relationships
    subject: "Subject" = Relationship(
        back_populates="organization_links", sa_relationship_kwargs={"lazy": "selectin"}
    )
    organization: "Organization" = Relationship(back_populates="subject_links")
    publickey: "PublicKey" = Relationship()


class SubjectOrganizationLinkCreate(SubjectOrganizationLinkBase):
    pass

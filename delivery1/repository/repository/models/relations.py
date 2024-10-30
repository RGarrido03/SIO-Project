import uuid

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field, Relationship

from repository.models.session import Session


class SubjectOrganizationLinkBase(SQLModel):
    subject_username: str = Field(foreign_key="subject.username", primary_key=True)
    organization_name: str = Field(foreign_key="organization.name", primary_key=True)
    public_key_id: uuid.UUID = Field(foreign_key="publickey.id")


class SubjectOrganizationLink(SubjectOrganizationLinkBase, table=True):
    session: Session | None = Field(default=None, sa_column=Column(JSONB))

    # Relationships
    subject: "Subject" = Relationship(back_populates="organization_links")
    organization: "Organization" = Relationship(back_populates="subject_links")
    publickey: "PublicKey" = Relationship()


class SubjectOrganizationLinkCreate(SubjectOrganizationLinkBase):
    pass

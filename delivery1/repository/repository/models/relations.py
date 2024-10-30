import uuid

from sqlmodel import SQLModel, Field, Relationship


class SubjectOrganizationLinkBase(SQLModel):
    subject_username: str = Field(foreign_key="subject.username", primary_key=True)
    organization_name: str = Field(foreign_key="organization.name", primary_key=True)
    public_key: uuid.UUID = Field(foreign_key="publickey.id")


class SubjectOrganizationLink(SubjectOrganizationLinkBase, table=True):
    subject: "Subject" = Relationship(back_populates="organization_links")
    organization: "Organization" = Relationship(back_populates="subject_links")


class SubjectOrganizationLinkCreate(SubjectOrganizationLinkBase):
    pass

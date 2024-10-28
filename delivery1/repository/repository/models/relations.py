import uuid

from sqlmodel import SQLModel, Field, Relationship


class SubjectOrganizationLink(SQLModel, table=True):
    subject_username: str = Field(foreign_key="subject.username", primary_key=True)
    organization_name: str = Field(foreign_key="organization.name", primary_key=True)
    public_key: uuid.UUID = Field(foreign_key="public_key.id")

    subject: "Subject" = Relationship(back_populates="organization_links")
    organization: "Organization" = Relationship(back_populates="subject_links")

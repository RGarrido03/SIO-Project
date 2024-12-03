import uuid

from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship

from repository.models.relations import SubjectOrganizationLink


class SubjectBase(SQLModel):
    username: str = Field(index=True, primary_key=True)
    full_name: str
    email: EmailStr = Field(index=True)


class Subject(SubjectBase, table=True):
    active: bool = Field(default=True)
    public_keys: list["PublicKey"] = Relationship(
        back_populates="subject", sa_relationship_kwargs={"lazy": "selectin"}
    )
    organization_links: list[SubjectOrganizationLink] = Relationship(
        back_populates="subject"
    )


class SubjectCreate(SubjectBase):
    public_key: str


class SubjectActiveListing(SQLModel):
    username: str
    full_name: str
    active: bool


class PublicKeyBase(SQLModel):
    key: str = Field(index=True)
    subject_username: str = Field(foreign_key="subject.username")


class PublicKey(PublicKeyBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    subject: Subject = Relationship(back_populates="public_keys")


class PublicKeyCreate(PublicKeyBase):
    pass


class SubjectWithPublicKeyUUID(SQLModel):
    subject: Subject
    public_key: PublicKey

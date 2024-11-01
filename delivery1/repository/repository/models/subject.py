import uuid

from pydantic import EmailStr
from sqlalchemy import Column, Enum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, SQLModel, Relationship

from repository.models.permission import (
    RoleEnum,
    RolePermission,
    OrganizationPermission,
)
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
    roles: list["SubjectRoleLink"] = Relationship(back_populates="subject")


class SubjectCreate(SubjectBase):
    public_key: str


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


class Role(SQLModel, table=True):
    name: RoleEnum = Field(index=True, primary_key=True)
    role_permissions: list[RolePermission] = Field(
        sa_column=Column(ARRAY(Enum(RolePermission)))
    )
    organization_permissions: list[OrganizationPermission] = Field(
        sa_column=Column(ARRAY(Enum(OrganizationPermission)))
    )
    subjects: list["SubjectRoleLink"] = Relationship(back_populates="role")


class SubjectRoleLink(SQLModel, table=True):
    subject_username: str = Field(foreign_key="subject.username", primary_key=True)
    role_name: RoleEnum = Field(foreign_key="role.name", primary_key=True)

    subject: Subject = Relationship(back_populates="roles")
    role: Role = Relationship(back_populates="subjects")

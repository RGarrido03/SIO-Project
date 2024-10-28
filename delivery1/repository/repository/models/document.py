import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field, Relationship

from repository.models.organization import Organization
from repository.models.permission import DocumentPermission, RoleEnum
from repository.models.subject import Subject


class DocumentBase(SQLModel):
    # Public metadata
    document_handle: str = Field(index=True, primary_key=True)
    name: str
    create_date: datetime.datetime = Field(default=datetime.datetime.now)
    file_handle: str

    # ACL
    acl: dict[RoleEnum, list[DocumentPermission]] = Field(
        default={}, sa_column=Column(JSONB)
    )

    # Relations
    organization_name: str = Field(foreign_key="organization.name")
    creator_username: str = Field(foreign_key="subject.username")
    deleter_username: str | None = Field(default=None, foreign_key="subject.username")


class DocumentBaseWithPrivateMeta(DocumentBase):
    alg: str
    key: str


class Document(DocumentBaseWithPrivateMeta, table=True):
    organization: Organization = Relationship(back_populates="documents")
    creator: Subject = Relationship(back_populates="documents")
    deleter: Subject | None = Relationship(back_populates="deleted_documents")


class DocumentCreate(DocumentBaseWithPrivateMeta):
    pass

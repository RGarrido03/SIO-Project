import uuid
from datetime import datetime

from sqlalchemy import Column, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field, Relationship

from repository.models.organization import Organization
from repository.models.permission import DocumentPermission, RoleEnum
from repository.models.subject import Subject


class DocumentBase(SQLModel):
    # Public metadata
    name: str
    create_date: datetime = Field(default=func.now())
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
    document_handle: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization: Organization = Relationship(back_populates="documents")
    creator: Subject = Relationship(back_populates="documents")
    deleter: Subject | None = Relationship(back_populates="deleted_documents")


class DocumentCreate(DocumentBaseWithPrivateMeta):
    pass

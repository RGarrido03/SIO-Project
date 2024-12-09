import uuid
from datetime import datetime

from sqlalchemy import Column, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import RelationshipProperty
from sqlmodel import SQLModel, Field, Relationship

from repository.models.organization import Organization
from repository.models.permission import DocumentPermission
from repository.models.subject import Subject


class DocumentBase(SQLModel):
    # Public metadata
    name: str = Field(index=True)
    file_handle: str | None

    # ACL
    acl: dict[str, set[DocumentPermission]] = Field(default={}, sa_column=Column(JSONB))

    # Relations
    organization_name: str = Field(foreign_key="organization.name")
    creator_username: str = Field(foreign_key="subject.username")
    deleter_username: str | None = Field(default=None, foreign_key="subject.username")


class DocumentBaseWithPrivateMeta(DocumentBase):
    alg: str
    key: str
    iv: str


class Document(DocumentBaseWithPrivateMeta, table=True):
    document_handle: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    create_date: datetime = Field(default=func.now())

    # Relations
    organization: Organization = Relationship(back_populates="documents")
    creator: Subject = Relationship(
        back_populates="documents",
        sa_relationship=RelationshipProperty(
            "Subject",
            primaryjoin="Document.creator_username == Subject.username",
        ),
    )
    deleter: Subject | None = Relationship(
        back_populates="deleted_documents",
        sa_relationship=RelationshipProperty(
            "Subject",
            primaryjoin="Document.deleter_username == Subject.username",
        ),
    )


class DocumentCreate(DocumentBaseWithPrivateMeta):
    file_handle: str


class DocumentCreateWithFile(DocumentCreate):
    file_content: str

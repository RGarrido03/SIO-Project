import uuid
from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import field_validator, field_serializer, WrapSerializer, PlainSerializer, model_serializer

from sqlalchemy import Column, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import RelationshipProperty, object_mapper
from sqlmodel import SQLModel, Field, Relationship

from repository.models.organization import Organization
from repository.models.permission import DocumentPermission, RoleEnum
from repository.models.subject import Subject
from repository.utils.serializers import SerializableSet




class DocumentBase(SQLModel):
    # Public metadata
    name: str = Field(index=True)
    file_handle: str | None

    # ACL
    acl:  dict[RoleEnum, SerializableSet[DocumentPermission]] = Field(
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


    # model_config = {
    #     "json_encoders": {
    #         set: list,
    #         RoleEnum: lambda x: x.value,
    #         DocumentPermission: lambda x: x.value
    #     }
    # }
    #
    # def model_dump(self, *args, **kwargs):
    #     result = super().model_dump(*args, **kwargs)
    #     if "acl" in result:
    #         result["acl"] = {
    #             role.value if isinstance(role, RoleEnum) else role:
    #                 [perm.value if isinstance(perm, DocumentPermission) else perm for perm in perms]
    #             for role, perms in result["acl"].items()
    #         }
    #     return result
    #
    # def model_dump_json(
    #     self,
    #     *,
    #     indent: int | None = None,
    #     include: IncEx | None = None,
    #     exclude: IncEx | None = None,
    #     context: Any | None = None,
    #     by_alias: bool = False,
    #     exclude_unset: bool = False,
    #     exclude_defaults: bool = False,
    #     exclude_none: bool = False,
    #     round_trip: bool = False,
    #     warnings: bool | Literal['none', 'warn', 'error'] = True,
    #     serialize_as_any: bool = False,
    # ) -> str:
    #     return self.__class__.model_config["json_encoders"].get(set, list)(self.model_dump())


class DocumentCreate(DocumentBaseWithPrivateMeta):
    file_handle: str

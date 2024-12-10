from typing import TYPE_CHECKING

from sqlalchemy import Enum, Column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, SQLModel, Relationship

from repository.models.permission import Permission
from repository.models.relations import SubjectOrganizationLink
from repository.models.subject import SubjectCreate

if TYPE_CHECKING:
    from repository.models.document import Document


class OrganizationBase(SQLModel):
    name: str = Field(index=True, primary_key=True)


class Organization(OrganizationBase, table=True):
    subject_links: list[SubjectOrganizationLink] = Relationship(
        back_populates="organization"
    )
    documents: list["Document"] = Relationship(back_populates="organization")
    roles: list["OrganizationRole"] = Relationship(back_populates="organization")


class OrganizationCreate(SQLModel):
    organization: OrganizationBase
    subject: SubjectCreate


class OrganizationRoleBase(SQLModel):
    organization_name: str = Field(foreign_key="organization.name", primary_key=True)
    role: str = Field(index=True, primary_key=True)
    active: bool = Field(default=True)
    permissions: set[Permission] = Field(
        default_factory=set, sa_column=Column(ARRAY(Enum(Permission)))
    )


class OrganizationRole(OrganizationRoleBase, table=True):
    organization: Organization = Relationship(back_populates="roles")

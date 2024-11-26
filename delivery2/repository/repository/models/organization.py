from typing import TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

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
    documents: list[Document] = Relationship(back_populates="organization")


class OrganizationCreate(SQLModel):
    organization: OrganizationBase
    subject: SubjectCreate

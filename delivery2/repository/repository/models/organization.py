from sqlmodel import Field, SQLModel, Relationship

from repository.models.subject import SubjectOrganizationLink, SubjectCreate


class OrganizationBase(SQLModel):
    name: str = Field(index=True, primary_key=True)


class Organization(OrganizationBase, table=True):
    subject_links: list[SubjectOrganizationLink] = Relationship(
        back_populates="organization"
    )
    documents: list["Document"] = Relationship(back_populates="organization")


class OrganizationCreate(SQLModel):
    organization: OrganizationBase
    subject: SubjectCreate

from sqlmodel import Field, SQLModel, Relationship

from repository.models.subject import SubjectOrganizationLink


class OrganizationBase(SQLModel):
    name: str = Field(index=True, primary_key=True)


class Organization(OrganizationBase, table=True):
    subject_links: list[SubjectOrganizationLink] = Relationship(
        back_populates="organization"
    )


class OrganizationCreate(OrganizationBase):
    pass

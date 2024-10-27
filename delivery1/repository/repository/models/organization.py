from sqlmodel import Field, SQLModel, Relationship

from repository.models.subject import UserOrganizationLink


class OrganizationBase(SQLModel):
    name: str = Field(index=True, primary_key=True)


class Organization(OrganizationBase, table=True):
    subject_links: list["UserOrganizationLink"] = Relationship(
        back_populates="organization"
    )


class OrganizationCreate(OrganizationBase):
    pass

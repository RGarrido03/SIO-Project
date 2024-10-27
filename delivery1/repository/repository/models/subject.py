from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship

from repository.models.relations import UserOrganizationLink


class SubjectBase(SQLModel):
    username: str = Field(index=True, primary_key=True)
    full_name: str
    email: EmailStr = Field(index=True)


class Subject(SubjectBase, table=True):
    public_keys: list["PublicKey"] = Relationship(back_populates="subject")
    organization_links: list["UserOrganizationLink"] = Relationship(
        back_populates="subject"
    )


class SubjectCreate(SubjectBase):
    pass


class PublicKey(SQLModel, table=True):
    key: str = Field(index=True, primary_key=True)
    subject_username: str = Field(foreign_key="subject.username")
    subject: Subject = Relationship(back_populates="public_keys")

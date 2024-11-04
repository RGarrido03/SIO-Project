import uuid
from datetime import datetime, timedelta

from sqlmodel import SQLModel, Field

from repository.models.nested_base import MutableSABaseModel
from repository.models.permission import RoleEnum


# Use of Session is on file repository/models/relations.py


class Session(MutableSABaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    keys: list[str]
    expires: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(minutes=30)
    )
    roles: set[RoleEnum] = Field(default_factory=set)


class SessionWithSubjectInfo(Session):
    username: str
    organization: str


class SessionCreate(SQLModel):
    organization: str
    username: str
    password: str
    credentials: str

import uuid
from datetime import datetime, timedelta

from sqlmodel import SQLModel, Field


# Use of Session is on file repository/models/relations.py


class Session(SQLModel):
    id: uuid.UUID = Field(default=uuid.uuid4)
    keys: list[str]
    expires: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(minutes=30)
    )


class SessionCreate(SQLModel):
    organization: str
    username: str
    password: str
    private: str
    public: str

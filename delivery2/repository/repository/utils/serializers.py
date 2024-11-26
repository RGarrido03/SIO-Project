from typing import Set, Any

from pydantic import BaseModel


class SerializableSet[T](BaseModel):
    items: Set[T]

    def __init__(self, items: set[T], **kwargs: Any) -> None:
        super().__init__(items=items, **kwargs)

    class Config:
        json_encoders = {set: lambda v: list(v)}

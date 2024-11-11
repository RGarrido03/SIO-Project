from typing import Set, Any, TypeVar
from pydantic import BaseModel
from typing_extensions import Generic

T = TypeVar('T')
class SerializableSet(BaseModel, Generic[T]):
    items: Set[T]

    def __init__(self, items: set, **kwargs):
        super().__init__(items=items, **kwargs)

    class Config:
        json_encoders = {
            set: lambda v: list(v)
        }
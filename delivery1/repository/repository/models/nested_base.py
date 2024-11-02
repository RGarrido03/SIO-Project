from typing import Any, Self, Optional

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel as _BaseModel
from sqlalchemy import types, Dialect
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.sql.type_api import TypeEngine


class JSONBPydanticField(types.TypeDecorator):
    impl = JSONB

    def __init__(
        self,
        pydantic_model_class: type["MutableSABaseModel"],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.pydantic_model_class = pydantic_model_class

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[JSONB]:
        return dialect.type_descriptor(JSONB())

    def process_bind_param(self, value: _BaseModel, dialect: Dialect) -> str:
        return jsonable_encoder(value) if value else None

    def process_result_value(
        self, value: dict[str, Any] | None, dialect: Dialect
    ) -> Optional["MutableSABaseModel"]:
        return (
            self.pydantic_model_class.model_validate(value)
            if value is not None
            else None
        )


class MutableSABaseModel(_BaseModel, Mutable):

    def __setattr__(self, name: str, value: Any) -> None:
        self.changed()
        return super().__setattr__(name, value)

    @classmethod
    def coerce(cls, key: str, value: Any) -> Self | None:
        if isinstance(value, cls) or value is None:
            return value

        if isinstance(value, str):
            return cls.model_validate_json(value)

        if isinstance(value, dict):
            return cls.model_validate(value)

        return super().coerce(key, value)

    @classmethod
    def to_sa_type(cls) -> JSONBPydanticField:
        return cls.as_mutable(JSONBPydanticField(cls))

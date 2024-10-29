import uuid
from typing import Generic, TypeVar, Type

from sqlmodel import select, SQLModel

from repository.config.database import get_session

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
PrimaryKeyType = TypeVar("PrimaryKeyType", int, str, uuid.UUID)


class CRUDBase(Generic[ModelType, CreateSchemaType, PrimaryKeyType]):
    def __init__(
        self,
        model: Type[ModelType],
    ):
        """
        Default methods to Create, Read, Update & Delete (CRUD).

        :param model: The SQLModel model to use.
        :type model: SQLModel
        """
        self.model = model

    async def create(self, obj: CreateSchemaType) -> ModelType:
        session = await anext(get_session())
        db_obj = self.model.model_validate(obj)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get(self, id: PrimaryKeyType) -> ModelType | None:
        session = await anext(get_session())
        return await session.get(self.model, id)

    async def get_all(self) -> list[ModelType]:
        session = await anext(get_session())
        result = await session.exec(select(self.model))
        return list(result.all())

    async def update(
        self, id: PrimaryKeyType, obj: CreateSchemaType
    ) -> ModelType | None:
        db_obj = await self.get(id)
        if db_obj is None:
            return None

        session = await anext(get_session())
        new_data = obj.model_dump(exclude_unset=True)
        db_obj.sqlmodel_update(new_data)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(self, id: PrimaryKeyType) -> bool:
        obj = await self.get(id)
        if obj is None:
            return False

        session = await anext(get_session())
        await session.delete(obj)
        await session.commit()
        return True

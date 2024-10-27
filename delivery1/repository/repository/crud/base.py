from typing import Generic, TypeVar, Type, Annotated

from fastapi import Depends
from sqlmodel import select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from repository.config.database import get_session

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)

Session = Annotated[AsyncSession, Depends(get_session)]


class CRUDBase(Generic[ModelType, CreateSchemaType]):
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

    async def create(self, obj: CreateSchemaType, session: Session) -> ModelType:
        db_obj = self.model.model_validate(obj)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get(self, id: int, session: Session) -> ModelType | None:
        return await session.get(self.model, id)

    async def get_all(self, session: Session) -> list[ModelType]:
        result = await session.exec(select(self.model))
        return list(result.all())

    async def update(
        self, id: int, obj: CreateSchemaType, session: Session
    ) -> ModelType | None:
        db_obj = await self.get(id, session)
        if db_obj is None:
            return None

        new_data = obj.model_dump(exclude_unset=True)
        db_obj.sqlmodel_update(new_data)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(self, id: int, session: Session) -> bool:
        obj = await self.get(id, session)
        if obj is None:
            return False

        await session.delete(obj)
        await session.commit()
        return True

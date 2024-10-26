from typing import Generic, TypeVar, Type

from fastapi import HTTPException
from sqlmodel import select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
PrimaryKeyType = TypeVar("PrimaryKeyType", int)


class CRUDBase(Generic[ModelType, CreateSchemaType, PrimaryKeyType]):
    def __init__(
        self,
        model: Type[ModelType],
        not_found_exception: HTTPException,
    ):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        :param model: The SQLModel model to use.
        :type model: SQLModel
        :param not_found_exception: The exception to raise when the object is not found.
        :type not_found_exception: HTTPException
        """
        self.model = model
        self.not_found_exception = not_found_exception

    async def create(self, obj: CreateSchemaType, session: AsyncSession) -> ModelType:
        obj1 = self.model(**obj.model_dump())
        session.add(obj1)
        await session.commit()
        await session.refresh(obj1)
        return obj1

    async def get(
        self,
        id: PrimaryKeyType,
        session: AsyncSession,
        exception_if_not_found: bool = True,
    ) -> ModelType:
        obj: ModelType | None = await session.get(self.model, id)
        if not obj and exception_if_not_found:
            raise self.not_found_exception
        return obj  # type: ignore

    async def get_all(self, session: AsyncSession) -> list[ModelType]:
        result = await session.exec(select(self.model))
        return list(result.all())

    async def update(
        self,
        id: PrimaryKeyType,
        obj: CreateSchemaType,
        session: AsyncSession,
        db_obj: ModelType | None = None,
    ) -> ModelType:
        if not db_obj:
            db_obj = await self.get(id, session)

        for key, value in obj.model_dump().items():
            setattr(db_obj, key, value)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def create_or_update(
        self, id: PrimaryKeyType, obj: CreateSchemaType, session: AsyncSession
    ) -> ModelType:
        result = await self.get(id, session, exception_if_not_found=False)

        if result:
            return await self.update(id, obj, session, db_obj=result)

        return await self.create(obj, session)

    async def delete(self, id: PrimaryKeyType, session: AsyncSession) -> bool:
        obj = await self.get(id, session)
        await session.delete(obj)
        await session.commit()
        return True

from typing import Generic, TypeVar, Type, Annotated

from fastapi import Depends
from sqlmodel import select, SQLModel, Session as SQLModelSession

from repository.config.database import get_session

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)

Session = Annotated[SQLModelSession, Depends(get_session)]


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

    def create(self, obj: CreateSchemaType, session: Session) -> ModelType:
        obj1 = self.model(**obj.model_dump())
        session.add(obj1)
        session.commit()
        session.refresh(obj1)
        return obj1

    def get(self, id: int, session: Session) -> ModelType | None:
        return session.get(self.model, id)  # type: ignore

    def get_all(self, session: Session) -> list[ModelType]:
        result = session.exec(select(self.model))
        return list(result.all())

    def update(
        self, id: int, obj: CreateSchemaType, session: Session
    ) -> ModelType | None:
        db_obj = self.get(id, session)
        if db_obj is None:
            return None

        for key, value in obj.model_dump().items():
            setattr(db_obj, key, value)

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def delete(self, id: int, session: Session) -> bool:
        obj = self.get(id, session)
        if obj is None:
            return False

        session.delete(obj)
        session.commit()
        return True

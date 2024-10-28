from typing import AsyncGenerator

from alembic import command, config
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from repository.config.settings import settings

engine = AsyncEngine(create_engine(settings.DATABASE_URI, future=True))


def run_upgrade(connection: Connection, cfg: config.Config) -> None:
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(run_upgrade, config.Config("alembic.ini"))


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

from typing import Generator

from alembic import command, config
from sqlalchemy import Connection
from sqlmodel import create_engine, Session

from repository.config.settings import settings

engine = create_engine(settings.DATABASE_URI, connect_args={"check_same_thread": False})


def run_upgrade(connection: Connection, cfg: config.Config) -> None:
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


async def init_db() -> None:
    with engine.begin() as conn:
        run_upgrade(conn, config.Config("alembic.ini"))


def get_session() -> Generator[Session, None]:
    with Session(engine) as session:  # type: ignore
        yield session

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.engine import Engine

from ..core.config import settings

engine: Engine = create_engine(settings.DATABASE_URL, echo=False)


def init_db() -> None:
    from ..models import *  # noqa: F401,F403 — register all models
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
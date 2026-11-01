from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from ..core.config import settings

engine: Engine = create_engine(settings.DATABASE_URL, echo=False)


def init_db() -> None:
    from .. import models  # noqa: F401 — triggers __init__.py imports registering tables
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session

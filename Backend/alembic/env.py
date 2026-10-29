from logging.config import fileConfig
import os
import sys

# Add the backend dir to the path so we can import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlmodel import SQLModel

# Import all models so Alembic can detect them
from src.models import *  # noqa: F401,F403

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

# Get the database URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sorax_dev.db")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")


def run_migrations_offline() -> None:
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        url=DATABASE_URL,
        target_metadata=target_metadata,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
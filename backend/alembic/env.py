"""Alembic migration environment configuration."""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from app.database import Base
from app.models.user import User
from app.models.technician import Technician

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set up the SQLAlchemy URL from environment variable or use default
sqlalchemy_url = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/sevaihub"
)
config.set_main_option("sqlalchemy.url", sqlalchemy_url)

# Add all SQLAlchemy models for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/sevaihub"
    )

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

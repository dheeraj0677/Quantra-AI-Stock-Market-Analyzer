"""
Alembic migration environment — async configuration.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings
from app.db.base import Base  # noqa: F401 — ensures models are imported
from app.models.alert import Alert  # noqa: F401
from app.models.backtest import BacktestRun  # noqa: F401
from app.models.news_article import NewsArticle  # noqa: F401
from app.models.portfolio import Portfolio, Position  # noqa: F401
from app.models.prediction import Prediction, PredictionFactor  # noqa: F401
from app.models.stock_meta import StockMeta  # noqa: F401

# Import all models so Alembic can detect them
from app.models.user import User  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — generates SQL without DB connection."""
    url = get_settings().DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Helper to configure context and execute migrations."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode — connects to the DB."""
    connectable = create_async_engine(
        get_settings().DATABASE_URL,
        pool_pre_ping=True,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

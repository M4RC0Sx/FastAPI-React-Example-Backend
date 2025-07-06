from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from fastapi_react_example_backend.core.config import settings


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


engine = create_async_engine(str(settings.POSTGRES_ASYNC_URI), pool_pre_ping=True)
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        yield session

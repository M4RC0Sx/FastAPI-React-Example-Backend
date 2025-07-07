from __future__ import annotations

from typing import TYPE_CHECKING

import pytest_asyncio

from httpx import ASGITransport
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from fastapi_react_example_backend.db.session import get_session
from fastapi_react_example_backend.main import app


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


TEST_DATABASE_URI = "sqlite+aiosqlite:///:memory:"
TEST_ENGINE = create_async_engine(
    TEST_DATABASE_URI, connect_args={"check_same_thread": False}
)

TestSessionFactory = async_sessionmaker(
    autocommit=False,
    expire_on_commit=False,
    autoflush=False,
    bind=TEST_ENGINE,
    class_=AsyncSession,
)


@pytest_asyncio.fixture(scope="session")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    app.dependency_overrides[get_session] = lambda: db_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db() -> AsyncGenerator[None]:
    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield

    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
async def db_session(setup_db: None) -> AsyncGenerator[AsyncSession]:
    async with TestSessionFactory() as session:
        yield session
        await session.close()

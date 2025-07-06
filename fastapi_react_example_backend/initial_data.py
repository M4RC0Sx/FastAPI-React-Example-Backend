from __future__ import annotations

import structlog

from fastapi_react_example_backend.core.config import settings
from fastapi_react_example_backend.crud import user as user_crud
from fastapi_react_example_backend.db.session import AsyncSessionFactory
from fastapi_react_example_backend.models.user import UserCreate


logger = structlog.get_logger(__name__)


async def init_db() -> None:
    async with AsyncSessionFactory() as session:
        user = await user_crud.get_user_by_email(
            session=session, email=settings.ADMIN_EMAIL
        )
        if user:
            logger.ingo("Admin user already exists, skipping creation.")
            return

        user_create = UserCreate(
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD,
            full_name="Admin User",
        )
        await user_crud.create_user(
            session=session,
            user_create=user_create,
            is_admin=True,
        )
        logger.info("Admin user created successfully.", email=settings.ADMIN_EMAIL)


async def main() -> None:
    logger.info("Initializing database with initial data...")
    await init_db()
    logger.info("Database initialization complete.")

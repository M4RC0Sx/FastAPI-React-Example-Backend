from __future__ import annotations

import secrets

from datetime import UTC
from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING

from sqlmodel import select

from fastapi_react_example_backend.core.config import settings
from fastapi_react_example_backend.models.token import RefreshToken


if TYPE_CHECKING:
    import uuid

    from sqlalchemy.ext.asyncio import AsyncSession


async def create_refresh_token(
    *, session: AsyncSession, user_id: uuid.UUID
) -> RefreshToken:
    expires_delta = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    db_refresh_token = RefreshToken(
        token=secrets.token_urlsafe(64),
        expires_at=datetime.now(UTC) + expires_delta,
        user_id=user_id,
    )

    session.add(db_refresh_token)
    await session.commit()
    await session.refresh(db_refresh_token)
    return db_refresh_token


async def get_refresh_token(
    *, session: AsyncSession, token: str
) -> RefreshToken | None:
    statement = select(RefreshToken).where(RefreshToken.token == token)
    result = await session.execute(statement)
    return result.scalars().one_or_none()

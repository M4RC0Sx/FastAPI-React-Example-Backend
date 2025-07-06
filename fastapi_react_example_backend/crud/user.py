from __future__ import annotations

from typing import TYPE_CHECKING

from sqlmodel import select

from fastapi_react_example_backend.core.security import get_password_hash
from fastapi_react_example_backend.core.security import verify_password
from fastapi_react_example_backend.models.user import User
from fastapi_react_example_backend.models.user import UserCreate


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def authenticate(
    *, session: AsyncSession, email: str, password: str
) -> User | None:
    db_user = await get_user_by_email(session=session, email=email)
    if not db_user:
        return None

    if not verify_password(password, db_user.hashed_password):
        return None

    return db_user


async def create_user(
    *, session: AsyncSession, user_create: UserCreate, is_admin: bool = False
) -> User:
    db_user = User.model_validate(
        user_create,
        update={
            "is_admin": is_admin,
            "hashed_password": get_password_hash(user_create.password),
        },
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def get_user_by_email(*, session: AsyncSession, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    return result.scalars().first()

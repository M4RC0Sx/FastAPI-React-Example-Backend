from __future__ import annotations

from datetime import UTC
from datetime import datetime
from datetime import timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from fastapi_react_example_backend.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    subject: str | Any, expires_delta: timedelta | None = None
) -> str:
    if not expires_delta:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(UTC) + expires_delta
    to_encode = {"sub": str(subject), "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ACCESS_TOKEN_ALGORITHM
    )

    return encoded_jwt

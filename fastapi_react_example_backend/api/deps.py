from __future__ import annotations

import uuid

from typing import Annotated

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_react_example_backend.core.config import settings
from fastapi_react_example_backend.db.session import get_session
from fastapi_react_example_backend.models.token import TokenPayload
from fastapi_react_example_backend.models.user import User


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.ROUTER_API_V1_PREFIX}/auth/login/access-token"
)

SessionDep = Annotated[AsyncSession, Depends(get_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ACCESS_TOKEN_ALGORITHM]
        )
        token_data = TokenPayload(**payload)

    except (JWTError, ValidationError) as e:
        raise credentials_exception from e

    if not token_data.sub:
        raise credentials_exception

    try:
        user_id = uuid.UUID(token_data.sub)
    except ValueError as e:
        raise credentials_exception from e

    user = await session.get(User, user_id)
    if not user:
        raise credentials_exception

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_current_user_is_admin(current_user: CurrentUserDep) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access",
        )
    return current_user

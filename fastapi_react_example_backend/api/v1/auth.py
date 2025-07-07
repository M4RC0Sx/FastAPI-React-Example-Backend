from __future__ import annotations

from datetime import UTC
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm  # noqa: TC002

import fastapi_react_example_backend.crud.user as user_crud

from fastapi_react_example_backend.api.deps import SessionDep  # noqa: TC001
from fastapi_react_example_backend.core.security import create_access_token
from fastapi_react_example_backend.crud.token import create_refresh_token
from fastapi_react_example_backend.crud.token import get_refresh_token
from fastapi_react_example_backend.models.token import RefreshTokenRequest
from fastapi_react_example_backend.models.token import Token


router = APIRouter()


@router.post("/login/access-token", response_model=Token)
async def login_for_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = await user_crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.id, expires_delta=None)
    refresh_token = await create_refresh_token(session=session, user_id=user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token.token,
        token_type="bearer",
    )


@router.post("/login/refresh-token", response_model=Token)
async def refresh_access_token(
    request: RefreshTokenRequest, session: SessionDep
) -> Token:
    refresh_token_db = await get_refresh_token(
        session=session, token=request.refresh_token
    )
    if not refresh_token_db or refresh_token_db.expires_at < datetime.now(UTC):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    await session.delete(refresh_token_db)
    await session.commit()

    new_access_token = create_access_token(refresh_token_db.user_id, expires_delta=None)
    new_refresh_token_db = await create_refresh_token(
        session=session, user_id=refresh_token_db.user_id
    )

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token_db.token,
        token_type="bearer",
    )

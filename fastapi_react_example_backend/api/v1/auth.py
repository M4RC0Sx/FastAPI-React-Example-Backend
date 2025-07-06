from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm  # noqa: TC002

import fastapi_react_example_backend.crud.user as user_crud

from fastapi_react_example_backend.api.deps import SessionDep  # noqa: TC001
from fastapi_react_example_backend.core.security import create_access_token
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
            detail="Infvalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.id, expires_delta=None)
    # TODO: Create refresh token
    refresh_token = "dummy_refresh_token"  # Placeholder for refresh token logic

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )

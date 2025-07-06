from __future__ import annotations

from fastapi import APIRouter

from fastapi_react_example_backend.api.deps import CurrentUserDep  # noqa: TC001
from fastapi_react_example_backend.models.user import UserPublic


router = APIRouter()


@router.get("/me", response_model=UserPublic)
async def read_user_me(current_user: CurrentUserDep) -> UserPublic:
    return UserPublic.model_validate(current_user)

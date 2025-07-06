from __future__ import annotations

from fastapi import APIRouter

from . import auth  # noqa: TID252
from . import users  # noqa: TID252


router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"])

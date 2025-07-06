from __future__ import annotations

import uuid  # noqa: TC003

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import Column
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlmodel import Field
from sqlmodel import Relationship
from sqlmodel import SQLModel

from fastapi_react_example_backend.db.types import AwareDatetime


if TYPE_CHECKING:
    from fastapi_react_example_backend.models.user import User


class TokenPayload(SQLModel):
    sub: str | None = Field(default=None)


class Token(SQLModel):
    access_token: str = Field()
    refresh_token: str = Field()
    token_type: str = Field(default="bearer")


class RefreshToken(SQLModel, table=True):
    id: int = Field(primary_key=True)
    token: str = Field(index=True, unique=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    expires_at: datetime = Field(sa_column=Column(AwareDatetime, nullable=False))

    user: Mapped[User] = Relationship(
        sa_relationship=relationship("User", back_populates="refresh_tokens")
    )

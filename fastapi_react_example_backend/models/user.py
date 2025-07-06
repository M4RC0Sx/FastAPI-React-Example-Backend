from __future__ import annotations

import uuid

from typing import TYPE_CHECKING

from pydantic import EmailStr  # noqa: TC002
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlmodel import Field
from sqlmodel import Relationship
from sqlmodel import SQLModel


if TYPE_CHECKING:
    from fastapi_react_example_backend.models.token import RefreshToken


# TODO: Check if we should refactor this schemas into a schemas module


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_admin: bool = Field(default=False)
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(SQLModel):
    email: EmailStr | None = None
    is_admin: bool | None = None
    full_name: str | None = None
    password: str | None = None


class UserUpdateMe(SQLModel):
    email: EmailStr | None = None
    full_name: str | None = None


class UserUpdatePasswordMe(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field()

    refresh_tokens: Mapped[list[RefreshToken]] = Relationship(
        sa_relationship=relationship(
            "RefreshToken", back_populates="user", cascade="all, delete-orphan"
        )
    )


class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic] = Field(default_factory=list)
    count: int = Field(default=0)

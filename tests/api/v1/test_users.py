from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from fastapi import status

from fastapi_react_example_backend.core.config import settings
from fastapi_react_example_backend.crud import user as user_crud
from fastapi_react_example_backend.models.user import UserCreate


if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


pytestmark = pytest.mark.asyncio


async def test_read_user_me_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    # Create test user in our test db
    email = "testme@test.es"
    password = "testmepassword"
    full_name = "Test Me"
    user_create_db = UserCreate(email=email, password=password, full_name=full_name)
    await user_crud.create_user(session=db_session, user_create=user_create_db)

    # Login to get access token
    login_data = {
        "username": email,
        "password": password,
    }
    response_login = await client.post(
        f"{settings.ROUTER_API_V1_PREFIX}/auth/login/access-token", data=login_data
    )

    # Assert login is successful
    assert response_login.status_code == status.HTTP_200_OK

    # Make request to get user profile
    auth_headers = {
        "Authorization": f"Bearer {response_login.json()['access_token']}",
    }
    response_me = await client.get(
        f"{settings.ROUTER_API_V1_PREFIX}/users/me", headers=auth_headers
    )

    # Assert status 200
    assert response_me.status_code == status.HTTP_200_OK

    user_data = response_me.json()

    # Assert user data matches created user
    assert user_data["email"] == email
    assert user_data["full_name"] == full_name
    assert user_data["is_admin"] is False

    # Assert user ID is present
    assert "id" in user_data

    # Assert password or hashed_password is not present
    assert "password" not in user_data
    assert "hashed_password" not in user_data


async def test_read_user_me_error_no_token(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    # Make request without token
    response_me = await client.get(
        f"{settings.ROUTER_API_V1_PREFIX}/users/me", headers={}
    )

    # Assert status 401
    assert response_me.status_code == status.HTTP_401_UNAUTHORIZED


async def test_read_user_me_error_invalid_token(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    # Make request with invalid token
    auth_headers = {
        "Authorization": "Bearer invalid_token",
    }
    response_me = await client.get(
        f"{settings.ROUTER_API_V1_PREFIX}/users/me", headers=auth_headers
    )

    # Assert status 401
    assert response_me.status_code == status.HTTP_401_UNAUTHORIZED

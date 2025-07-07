from __future__ import annotations

from datetime import UTC
from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING

import pytest

from fastapi import status

from fastapi_react_example_backend.core.config import settings
from fastapi_react_example_backend.crud import token as token_crud
from fastapi_react_example_backend.crud import user as user_crud
from fastapi_react_example_backend.models.token import RefreshToken
from fastapi_react_example_backend.models.user import UserCreate


if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


pytestmark = pytest.mark.asyncio


async def test_login_for_access_token_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    # Create test user in our test db
    email = "test1@test.es"
    password = "test1password"
    user_create_db = UserCreate(email=email, password=password, full_name="Test User")
    await user_crud.create_user(session=db_session, user_create=user_create_db)

    # Send login request with our created user credentials
    login_data = {
        "username": email,
        "password": password,
    }
    response = await client.post(
        f"{settings.ROUTER_API_V1_PREFIX}/auth/login/access-token", data=login_data
    )

    # Assert status 200
    assert response.status_code == status.HTTP_200_OK

    token_data = response.json()

    # Assert all token fields are present
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert "token_type" in token_data

    # Assert token type is bearer
    assert token_data["token_type"] == "bearer"

    # Assert access and refresh tokens are not None
    assert token_data["access_token"] is not None
    assert token_data["refresh_token"] is not None


async def test_login_for_access_token_error_wrong_password(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    # Create test user in our test db
    email = "test2@test.es"
    password = "test1password"
    user_create_db = UserCreate(email=email, password=password, full_name="Test User")
    await user_crud.create_user(session=db_session, user_create=user_create_db)

    # Send login request with a wrong password
    login_data = {
        "username": email,
        "password": "wrong_password",
    }
    response = await client.post(
        f"{settings.ROUTER_API_V1_PREFIX}/auth/login/access-token", data=login_data
    )

    # Assert status 401
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_data = response.json()

    # Assert error message is present
    assert "detail" in response_data
    assert response_data["detail"] == "Invalid credentials"


async def test_login_for_access_token_error_user_not_found(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    # Send login request with a non-existing user
    login_data = {
        "username": "nonexist@test.es",
        "password": "somepassword",
    }
    response = await client.post(
        f"{settings.ROUTER_API_V1_PREFIX}/auth/login/access-token", data=login_data
    )

    # Assert status 401
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_data = response.json()

    # Assert error message is present
    assert "detail" in response_data
    assert response_data["detail"] == "Invalid credentials"


async def test_refresh_access_token_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    # Create test user in our test db
    email = "refresh@test.es"
    password = "refreshpassword"
    user_create_db = UserCreate(
        email=email, password=password, full_name="Refresh User"
    )
    user = await user_crud.create_user(session=db_session, user_create=user_create_db)

    # Create refresh token for the user
    refresh_token_db = await token_crud.create_refresh_token(
        session=db_session, user_id=user.id
    )

    # Send refresh token request
    refresh_token_data = {
        "refresh_token": refresh_token_db.token,
    }
    response = await client.post(
        f"{settings.ROUTER_API_V1_PREFIX}/auth/login/refresh-token",
        json=refresh_token_data,
    )

    # Assert status 200
    assert response.status_code == status.HTTP_200_OK

    token_data = response.json()

    # Assert all token fields are present
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert "token_type" in token_data

    # Assert token type is bearer
    assert token_data["token_type"] == "bearer"

    # Assert access and refresh tokens are not None
    assert token_data["access_token"] is not None
    assert token_data["refresh_token"] is not None

    # Assert new refresh token is different from the old one
    assert token_data["refresh_token"] != refresh_token_db.token


async def test_refresh_access_token_error_invalid_token(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    # Send refresh token request with an invalid token
    refresh_token_data = {
        "refresh_token": "invalid_token",
    }
    response = await client.post(
        f"{settings.ROUTER_API_V1_PREFIX}/auth/login/refresh-token",
        json=refresh_token_data,
    )

    # Assert status 401
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_data = response.json()

    # Assert error message is present
    assert "detail" in response_data
    assert response_data["detail"] == "Invalid or expired refresh token"


async def test_refresh_access_token_error_expired_token(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    # Create test user in our test db
    email = "refreshexpired@test.es"
    password = "refreshexpiredpassword"
    user_create_db = UserCreate(
        email=email, password=password, full_name="Refresh Expired User"
    )
    user = await user_crud.create_user(session=db_session, user_create=user_create_db)

    # Create expired refresh token for the user
    expired_refresh_token = RefreshToken(
        token="expired_token",
        expires_at=datetime.now(UTC) - timedelta(days=1),
        user_id=user.id,
    )
    db_session.add(expired_refresh_token)
    await db_session.commit()

    # Send refresh token request
    refresh_token_data = {
        "refresh_token": expired_refresh_token.token,
    }
    response = await client.post(
        f"{settings.ROUTER_API_V1_PREFIX}/auth/login/refresh-token",
        json=refresh_token_data,
    )

    # Assert status 401
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response_data = response.json()

    # Assert error message is present
    assert "detail" in response_data
    assert response_data["detail"] == "Invalid or expired refresh token"


async def test_refresh_access_token_error_reused_token(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    # Create test user in our test db
    email = "refreshreused@test.es"
    password = "refreshreusedpassword"
    user_create_db = UserCreate(
        email=email, password=password, full_name="Refresh Reused User"
    )
    user = await user_crud.create_user(session=db_session, user_create=user_create_db)

    # Create refresh token for the user
    refresh_token = await token_crud.create_refresh_token(
        session=db_session, user_id=user.id
    )

    # Send refresh token request twice
    refresh_token_data = {
        "refresh_token": refresh_token.token,
    }
    response_first_use = await client.post(
        f"{settings.ROUTER_API_V1_PREFIX}/auth/login/refresh-token",
        json=refresh_token_data,
    )
    response_second_use = await client.post(
        f"{settings.ROUTER_API_V1_PREFIX}/auth/login/refresh-token",
        json=refresh_token_data,
    )

    # Assert first use status 200
    assert response_first_use.status_code == status.HTTP_200_OK

    first_token_data = response_first_use.json()

    # Assert all token fields are present
    assert "access_token" in first_token_data
    assert "refresh_token" in first_token_data
    assert "token_type" in first_token_data

    # Assert token type is bearer
    assert first_token_data["token_type"] == "bearer"

    # Assert access and refresh tokens are not None
    assert first_token_data["access_token"] is not None
    assert first_token_data["refresh_token"] is not None

    # Assert second use status 401
    assert response_second_use.status_code == status.HTTP_401_UNAUTHORIZED

    response_data = response_second_use.json()

    # Assert error message is present
    assert "detail" in response_data
    assert response_data["detail"] == "Invalid or expired refresh token"

from __future__ import annotations

from fastapi_react_example_backend.core.security import get_password_hash
from fastapi_react_example_backend.core.security import verify_password


def test_password_hashing_and_verification() -> None:
    plain_password = "my_secure_password"
    hashed_password = get_password_hash(plain_password)

    assert hashed_password is not None
    assert plain_password != hashed_password
    assert verify_password(plain_password, hashed_password) is True
    assert verify_password("wrong_password", hashed_password) is False

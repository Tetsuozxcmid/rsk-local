import pytest
from pydantic import ValidationError
from pydantic.types import SecretStr

from schemas.user_schemas.user_register import UserRegister
from schemas.user_schemas.user_auth import UserAuth


def test_user_register_rejects_short_password():
    with pytest.raises(ValidationError):
        UserRegister(
            email="user@example.com",
            password=SecretStr("short"),
            first_name="Иван",
            last_name="Иванов",
        )


def test_user_register_and_auth_accept_valid_payload():
    reg = UserRegister(
        email="user@example.com",
        password=SecretStr("password123"),
        first_name="Иван",
        last_name="Иванов",
    )
    assert reg.email == "user@example.com"

    auth = UserAuth(login="user1", password=SecretStr("password123"))
    assert auth.login == "user1"

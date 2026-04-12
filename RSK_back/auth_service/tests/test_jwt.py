import pytest

from services.jwt import create_access_token, decode_token


@pytest.mark.asyncio
async def test_jwt_create_and_decode_roundtrip():
    token = await create_access_token({"sub": "42", "role": "student"})
    assert isinstance(token, str) and len(token) > 20

    payload = await decode_token(token)
    assert payload is not None
    assert payload.get("sub") == "42"
    assert payload.get("role") == "student"
    assert payload.get("exp") is not None


@pytest.mark.asyncio
async def test_jwt_decode_invalid_returns_none():
    assert await decode_token("not-a-valid.jwt.token") is None

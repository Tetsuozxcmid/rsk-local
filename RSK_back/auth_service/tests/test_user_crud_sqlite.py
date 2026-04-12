"""
Интеграция UserCRUD с SQLite в памяти (без PostgreSQL).
Блокировка email через pg_advisory заменена заглушкой.
"""

import pytest
from fastapi import HTTPException
from pydantic.types import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from cruds.users_crud.crud import UserCRUD
from db.base import Base
from db.models.user import User, UserRole
from schemas.user_schemas.user_register import UserRegister


def _stub_hash(password: str) -> str:
    return f"stub:{password}"


@pytest.fixture
def noop_email_lock(monkeypatch):
    async def _noop(db, normalized_email):
        return None

    monkeypatch.setattr(
        "cruds.users_crud.crud.UserCRUD._lock_email",
        staticmethod(_noop),
    )


@pytest.fixture
def stub_password_backend(monkeypatch):
    """Обходит bcrypt (актуально для среды вроде Python 3.14 + несовместимый bcrypt)."""

    class Stub:
        def get_password_hash(self, password: str) -> str:
            return f"stub:{password}"

        def verify_password(self, plain: str, hashed: str) -> bool:
            return bool(hashed) and hashed == f"stub:{plain}"

    stub = Stub()
    for mod in (
        "routes.users_router.auth_logic",
        "cruds.users_crud.crud",
        "db.models.user",
    ):
        monkeypatch.setattr(f"{mod}.pass_settings", stub, raising=True)


@pytest.fixture
async def sqlite_session(noop_email_lock, stub_password_backend):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_user_persists_and_sets_temp_login(sqlite_session: AsyncSession):
    data = UserRegister(
        email="newuser@example.com",
        password=SecretStr("password123"),
        first_name="Пётр",
        last_name="Петров",
    )
    user, token, temp_login = await UserCRUD.create_user(sqlite_session, data)

    assert user.id is not None
    assert user.email == "newuser@example.com"
    assert user.verified is False
    assert temp_login == f"user{user.id}"
    assert len(token) > 10


@pytest.mark.asyncio
async def test_create_user_duplicate_verified_email_raises(sqlite_session: AsyncSession):
    data = UserRegister(
        email="dup@example.com",
        password=SecretStr("password123"),
        name="Первый Пользователь",
    )
    first, _, _ = await UserCRUD.create_user(sqlite_session, data)
    first.verified = True
    first.hashed_password = _stub_hash("password123")
    await sqlite_session.commit()

    with pytest.raises(HTTPException) as exc:
        await UserCRUD.create_user(sqlite_session, data)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_check_user_success_when_verified(sqlite_session: AsyncSession):
    user = User(
        name="Анна",
        email="anna@example.com",
        login="anna",
        role=UserRole.STUDENT,
        verified=True,
        confirmation_token=None,
        hashed_password=_stub_hash("mypassword12"),
        auth_provider=None,
        provider_id=None,
    )
    sqlite_session.add(user)
    await sqlite_session.commit()

    result = await User.check_user("anna", "mypassword12", sqlite_session)
    assert result is not None
    assert result["email"] == "anna@example.com"
    assert result["id"] == user.id


@pytest.mark.asyncio
async def test_check_user_wrong_password_returns_none(sqlite_session: AsyncSession):
    user = User(
        name="Борис",
        email="boris@example.com",
        login="boris",
        role=UserRole.STUDENT,
        verified=True,
        confirmation_token=None,
        hashed_password=_stub_hash("rightpass12"),
        auth_provider=None,
        provider_id=None,
    )
    sqlite_session.add(user)
    await sqlite_session.commit()

    assert await User.check_user("boris", "wrongpassword", sqlite_session) is None


@pytest.mark.asyncio
async def test_check_user_unverified_returns_none(sqlite_session: AsyncSession):
    data = UserRegister(
        email="tmp@example.com",
        password=SecretStr("password123"),
        name="Временный",
    )
    await UserCRUD.create_user(sqlite_session, data)

    assert await User.check_user("user1", "password123", sqlite_session) is None

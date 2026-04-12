"""
Профиль пользователя: CRUD против SQLite в памяти (смена имени и т.д.).
"""

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from cruds.profile_crud import ProfileCRUD
from db.base import Base
from db.models.user import User
from db.models.user_enum import UserEnum
from schemas.user import ProfileUpdate


@pytest.fixture
async def profile_sqlite_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_update_my_profile_changes_name_irl(profile_sqlite_session: AsyncSession):
    profile_sqlite_session.add(
        User(
            id=1,
            username="u1",
            email="u1@example.com",
            NameIRL="Старое",
            Surname="Имя",
            Type=UserEnum.Student,
            is_learned=False,
        )
    )
    await profile_sqlite_session.commit()

    update = ProfileUpdate(NameIRL="НовоеИмя")
    updated = await ProfileCRUD.update_my_profile(
        profile_sqlite_session, update, user_id=1
    )
    assert updated.NameIRL == "НовоеИмя"


@pytest.mark.asyncio
async def test_update_my_profile_updates_surname_and_region(
    profile_sqlite_session: AsyncSession,
):
    profile_sqlite_session.add(
        User(
            id=2,
            username="u2",
            email="u2@example.com",
            NameIRL="Иван",
            Surname="Старых",
            Region="",
            Type=UserEnum.Teacher,
            is_learned=True,
        )
    )
    await profile_sqlite_session.commit()

    update = ProfileUpdate(Surname="Новых", Region="Татарстан")
    await ProfileCRUD.update_my_profile(profile_sqlite_session, update, user_id=2)

    from sqlalchemy import select

    res = await profile_sqlite_session.execute(select(User).where(User.id == 2))
    user = res.scalar_one()
    assert user.Surname == "Новых"
    assert user.Region == "Татарстан"


@pytest.mark.asyncio
async def test_update_my_profile_not_found_raises_404(profile_sqlite_session: AsyncSession):
    update = ProfileUpdate(NameIRL="X")
    with pytest.raises(HTTPException) as exc:
        await ProfileCRUD.update_my_profile(profile_sqlite_session, update, user_id=999)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_my_profile_returns_model(profile_sqlite_session: AsyncSession):
    profile_sqlite_session.add(
        User(
            id=3,
            username="reader",
            email="r@example.com",
            NameIRL="Читатель",
            Surname="Тестов",
            Type=UserEnum.Student,
            is_learned=False,
        )
    )
    await profile_sqlite_session.commit()

    out = await ProfileCRUD.get_my_profile(profile_sqlite_session, user_id=3)
    assert out.NameIRL == "Читатель"
    assert out.email == "r@example.com"
    assert out.is_learned is False

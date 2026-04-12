import pytest
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db.base import Base
from db.models.team_members import TeamMember
from db.models.teams import Team
from db.models.teams_enums.enums import DirectionEnum
from routes.teams_router.router import (
    delete_team,
    get_team_by_id,
    get_teams_count_by_region,
)
from starlette.testclient import TestClient

from main import app


@pytest.fixture
async def memory_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def memory_session(memory_engine):
    factory = async_sessionmaker(
        memory_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with factory() as session:
        yield session


@pytest.mark.asyncio
async def test_db_insert_team_and_query(memory_session):
    team = Team(
        name="Команда А",
        direction=DirectionEnum.science,
        description="Описание",
        region="Москва",
        organization_id=1,
        organization_name="Школа 1",
        leader_id=10,
        number_of_members=1,
    )
    memory_session.add(team)
    await memory_session.commit()
    await memory_session.refresh(team)

    assert team.id is not None
    result = await memory_session.execute(select(Team).where(Team.id == team.id))
    loaded = result.scalar_one()
    assert loaded.name == "Команда А"
    assert loaded.region == "Москва"


@pytest.mark.asyncio
async def test_db_team_member_foreign_key(memory_session):
    team = Team(
        name="Команда B",
        direction=DirectionEnum.sport,
        region="СПб",
        organization_id=2,
        organization_name="Школа 2",
        leader_id=20,
        number_of_members=2,
    )
    memory_session.add(team)
    await memory_session.commit()
    await memory_session.refresh(team)

    member = TeamMember(team_id=team.id, user_id=100, is_leader=True)
    memory_session.add(member)
    await memory_session.commit()

    res = await memory_session.execute(
        select(TeamMember).where(TeamMember.team_id == team.id)
    )
    m = res.scalar_one()
    assert m.user_id == 100
    assert m.is_leader is True


@pytest.mark.asyncio
async def test_handler_count_by_region_empty(memory_session):
    out = await get_teams_count_by_region(region=None, db=memory_session)
    assert out == []


@pytest.mark.asyncio
async def test_handler_count_by_region_with_filter(memory_session):
    memory_session.add_all(
        [
            Team(
                name="T1",
                direction=DirectionEnum.art,
                region="Урал",
                organization_id=1,
                organization_name="Org",
                leader_id=1,
                number_of_members=1,
            ),
            Team(
                name="T2",
                direction=DirectionEnum.art,
                region="Урал",
                organization_id=1,
                organization_name="Org",
                leader_id=2,
                number_of_members=1,
            ),
        ]
    )
    await memory_session.commit()

    data = await get_teams_count_by_region(region="Урал", db=memory_session)
    assert data["region"] == "Урал"
    assert data["teams_count"] == 2


@pytest.mark.asyncio
async def test_handler_delete_team_removes_row(memory_session):
    team = Team(
        name="Удалить",
        direction=DirectionEnum.other,
        region="X",
        organization_id=1,
        organization_name="Org",
        leader_id=99,
        number_of_members=0,
    )
    memory_session.add(team)
    await memory_session.commit()
    await memory_session.refresh(team)
    team_id = team.id

    msg = await delete_team(team_id=team_id, db=memory_session)
    assert "deleted" in msg["message"].lower()

    res = await memory_session.execute(select(Team).where(Team.id == team_id))
    assert res.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_handler_get_team_by_id_not_found(memory_session):
    with pytest.raises(HTTPException) as exc:
        await get_team_by_id(team_id=99999, db=memory_session)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_db_teams_aggregate_count_by_region(memory_session):
    memory_session.add_all(
        [
            Team(
                name="A",
                direction=DirectionEnum.science,
                region="R1",
                organization_id=1,
                organization_name="O",
                leader_id=1,
                number_of_members=1,
            ),
            Team(
                name="B",
                direction=DirectionEnum.science,
                region="R1",
                organization_id=1,
                organization_name="O",
                leader_id=2,
                number_of_members=1,
            ),
            Team(
                name="C",
                direction=DirectionEnum.science,
                region="R2",
                organization_id=1,
                organization_name="O",
                leader_id=3,
                number_of_members=1,
            ),
        ]
    )
    await memory_session.commit()

    q = (
        select(Team.region, func.count(Team.id))
        .group_by(Team.region)
        .order_by(func.count(Team.id).desc())
    )
    result = await memory_session.execute(q)
    rows = result.all()
    assert len(rows) == 2
    by_reg = {r[0]: r[1] for r in rows}
    assert by_reg["R1"] == 2
    assert by_reg["R2"] == 1


def test_openapi_still_available():
    with TestClient(app) as client:
        r = client.get("/openapi.json")
    assert r.status_code == 200

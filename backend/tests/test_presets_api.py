import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.services.auth import hash_password, create_access_token
from app.services.presets import get_classic_single_column_preset

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        user_a = User(
            id="user_a_id",
            email="user_a@example.com",
            hashed_password=hash_password("passA"),
            full_name="User A",
        )
        user_b = User(
            id="user_b_id",
            email="user_b@example.com",
            hashed_password=hash_password("passB"),
            full_name="User B",
        )
        session.add(user_a)
        session.add(user_b)
        await session.commit()
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client_a(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(user_id="user_a_id", email="user_a@example.com")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers={"Authorization": f"Bearer {token}"}) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client_b(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(user_id="user_b_id", email="user_b@example.com")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers={"Authorization": f"Bearer {token}"}) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_presets_system_and_user_custom(client_a, client_b):
    # 1. Verify 8 system presets
    res_list = await client_a.get("/api/templates/presets")
    assert res_list.status_code == 200
    presets = res_list.json()
    assert len(presets) == 8
    expected_ids = {
        "classic-single-column",
        "modern-sidebar-left",
        "executive-sidebar-right",
        "header-banner",
        "compact-dense",
        "creative-accent",
        "minimal-editorial",
        "academic-cv",
    }
    actual_ids = {p["id"] for p in presets}
    assert expected_ids == actual_ids

    # 2. Get specific preset
    single_res = await client_a.get("/api/templates/presets/header-banner")
    assert single_res.status_code == 200
    assert single_res.json()["name"] == "Header Banner"
    assert single_res.json()["style"]["decorations"]["headerBanner"] is True

    # 3. Save as user custom template
    custom_style = get_classic_single_column_preset().model_dump()
    custom_style["colors"]["accent"] = "#9333ea"  # Custom purple
    save_res = await client_a.post(
        "/api/templates/user-presets",
        json={
            "name": "My Purple Minimal",
            "style_tokens": custom_style,
            "source_template_id": "classic-single-column",
        },
    )
    assert save_res.status_code == 201
    user_p = save_res.json()
    user_p_id = user_p["id"]
    assert user_p["name"] == "My Purple Minimal"

    # 4. List user custom presets
    user_list = await client_a.get("/api/templates/user-presets")
    assert user_list.status_code == 200
    assert len(user_list.json()) == 1
    assert user_list.json()[0]["id"] == user_p_id

    # 5. User B should have 0 custom presets and cannot delete User A's preset
    b_list = await client_b.get("/api/templates/user-presets")
    assert len(b_list.json()) == 0

    b_del = await client_b.delete(f"/api/templates/user-presets/{user_p_id}")
    assert b_del.status_code == 404

    # 6. User A deletes their preset
    del_res = await client_a.delete(f"/api/templates/user-presets/{user_p_id}")
    assert del_res.status_code == 204

    after_del = await client_a.get("/api/templates/user-presets")
    assert len(after_del.json()) == 0

import io
import json
import zipfile
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from sqlalchemy import select

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.resume import Document
from app.models.user_preset import UserStylePreset
from app.models.ai_log import AiUsageLog
from app.services.auth import hash_password, create_access_token

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
        user = User(
            id="user_harden_id",
            email="harden@example.com",
            hashed_password=hash_password("OldPassword123!"),
            full_name="Hardened User",
        )
        session.add(user)
        await session.commit()
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(user_id="user_harden_id", email="harden@example.com")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def public_client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_change_password(client, public_client):
    # 1. Attempt with incorrect current password -> 400
    res_bad = await client.post(
        "/api/account/password",
        json={"current_password": "WrongPassword!", "new_password": "NewPassword123!"},
    )
    assert res_bad.status_code == 400

    # 2. Update with valid current password -> 200
    res_good = await client.post(
        "/api/account/password",
        json={"current_password": "OldPassword123!", "new_password": "NewPassword123!"},
    )
    assert res_good.status_code == 200

    # 3. Verify sign in works with new password
    login_res = await public_client.post(
        "/api/auth/login",
        json={"email": "harden@example.com", "password": "NewPassword123!"},
    )
    assert login_res.status_code == 200


@pytest.mark.asyncio
async def test_forgot_and_reset_password(public_client):
    # 1. Request forgot password
    res_forgot = await public_client.post(
        "/api/auth/forgot-password",
        json={"email": "harden@example.com"},
    )
    assert res_forgot.status_code == 200
    data = res_forgot.json()
    reset_token = data.get("reset_token")
    assert reset_token is not None

    # 2. Reset password with token
    res_reset = await public_client.post(
        "/api/auth/reset-password",
        json={"reset_token": reset_token, "new_password": "ResetPassword456!"},
    )
    assert res_reset.status_code == 200

    # 3. Log in with newly reset password
    login_res = await public_client.post(
        "/api/auth/login",
        json={"email": "harden@example.com", "password": "ResetPassword456!"},
    )
    assert login_res.status_code == 200


@pytest.mark.asyncio
async def test_gdpr_data_export(client, db_session):
    # Seed user document, preset, and ai log
    doc = Document(
        id="doc_gdpr_1",
        user_id="user_harden_id",
        title="GDPR Test Resume",
        content={"header": {"name": "GDPR Subject"}, "sections": []},
        style={"templateId": "classic-single-column"},
    )
    preset = UserStylePreset(
        id="preset_gdpr_1",
        user_id="user_harden_id",
        name="Custom Neon Preset",
        style_tokens={"colors": {"accent": "#00ffcc"}},
    )
    ai_log = AiUsageLog(
        id="log_gdpr_1",
        user_id="user_harden_id",
        action="bullet_improve",
        tokens_in=50,
        tokens_out=60,
        cost_usd=0.0003,
    )
    db_session.add(doc)
    db_session.add(preset)
    db_session.add(ai_log)
    await db_session.commit()

    # Call GDPR export
    resp = await client.get("/api/account/export-data")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"

    # Verify contents of zip
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        names = zf.namelist()
        assert "profile.json" in names
        assert "presets/user_presets.json" in names
        assert "ai_usage/logs.json" in names

        # Read profile
        prof_json = json.loads(zf.read("profile.json").decode())
        assert prof_json["email"] == "harden@example.com"


@pytest.mark.asyncio
async def test_delete_account_cascade(client, public_client, db_session):
    # 1. Attempt delete with wrong password -> 400
    bad_del = await client.post("/api/account/delete", json={"password": "WrongPassword"})
    assert bad_del.status_code == 400

    # 2. Delete with correct password -> 200
    good_del = await client.post("/api/account/delete", json={"password": "OldPassword123!"})
    assert good_del.status_code == 200

    # 3. Confirm user is deleted from database
    stmt = select(User).where(User.id == "user_harden_id")
    res = await db_session.execute(stmt)
    assert res.scalar_one_or_none() is None

    # 4. Login now fails with 401
    login_res = await public_client.post(
        "/api/auth/login",
        json={"email": "harden@example.com", "password": "OldPassword123!"},
    )
    assert login_res.status_code == 401

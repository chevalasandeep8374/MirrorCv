import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.resume import Document
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
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client_b(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(user_id="user_b_id", email="user_b@example.com")
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
async def test_sharing_workflow(client_a, client_b, public_client):
    # 1. Create Resume for User A
    res_create = await client_a.post(
        "/api/resumes",
        json={
            "title": "Public Alex Resume",
            "content": {"header": {"name": "Alex Public"}, "sections": []},
            "style": {"templateId": "classic-single-column"},
        },
    )
    assert res_create.status_code == 201
    resume_id = res_create.json()["id"]

    # 2. Get initial share settings
    res_share = await client_a.get(f"/api/resumes/{resume_id}/share")
    assert res_share.status_code == 200
    share_info = res_share.json()
    assert share_info["is_active"] is False
    slug = share_info["slug"]
    assert len(slug) >= 12

    # 3. Public request while inactive returns 404
    pub_res = await public_client.get(f"/api/public/resumes/{slug}")
    assert pub_res.status_code == 404

    # 4. Enable sharing with password & noindex
    update_share = await client_a.post(
        f"/api/resumes/{resume_id}/share",
        json={
            "is_active": True,
            "password": "secret-password",
            "allow_pdf_download": True,
            "no_index": True,
        },
    )
    assert update_share.status_code == 200
    assert update_share.json()["is_active"] is True
    assert update_share.json()["has_password"] is True

    # 5. Public access without password prompts for password
    pub_req_no_pw = await public_client.get(f"/api/public/resumes/{slug}")
    assert pub_req_no_pw.status_code == 200
    body_no_pw = pub_req_no_pw.json()
    assert body_no_pw["password_required"] is True
    assert body_no_pw["content"] is None

    # 6. Public access with correct password returns document content + noindex header
    pub_req_pw = await public_client.get(
        f"/api/public/resumes/{slug}",
        headers={"X-Share-Password": "secret-password", "User-Agent": "Mozilla/5.0 (iPhone)"},
    )
    assert pub_req_pw.status_code == 200
    assert pub_req_pw.headers.get("x-robots-tag") == "noindex, nofollow"
    body_pw = pub_req_pw.json()
    assert body_pw["password_required"] is False
    assert body_pw["content"]["header"]["name"] == "Alex Public"

    # 7. Check view count incremented
    check_stats = await client_a.get(f"/api/resumes/{resume_id}/share")
    assert check_stats.json()["view_count"] == 1
    assert check_stats.json()["last_viewed_at"] is not None

    # 8. User B cannot access User A's share configuration (403/404)
    res_b = await client_b.get(f"/api/resumes/{resume_id}/share")
    assert res_b.status_code in (403, 404)

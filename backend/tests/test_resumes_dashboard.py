import pytest
import pytest_asyncio
import os
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User
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
        # Create User A and User B
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
async def test_dashboard_crud_and_multi_resume(client_a, client_b):
    # 1. Create Resume 1 with tags and folder
    create_res1 = await client_a.post(
        "/api/resumes",
        json={
            "title": "Backend Lead Resume",
            "target_job_title": "Principal Backend Architect",
            "tags": ["python", "lead", "remote"],
            "folder": "Big Tech 2026",
        },
    )
    assert create_res1.status_code == 201
    r1 = create_res1.json()
    r1_id = r1["id"]
    assert r1["title"] == "Backend Lead Resume"
    assert r1["target_job_title"] == "Principal Backend Architect"
    assert "python" in r1["tags"]
    assert r1["folder"] == "Big Tech 2026"

    # 2. Create Resume 2 (different folder and tag)
    create_res2 = await client_a.post(
        "/api/resumes",
        json={
            "title": "Fullstack Generalist",
            "target_job_title": "Fullstack Engineer",
            "tags": ["typescript", "react"],
            "folder": "Startups",
        },
    )
    assert create_res2.status_code == 201
    r2_id = create_res2.json()["id"]

    # 3. List Resumes
    list_res = await client_a.get("/api/resumes")
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) == 2

    # 4. Filter by folder
    folder_res = await client_a.get("/api/resumes?folder=Startups")
    assert folder_res.status_code == 200
    f_items = folder_res.json()
    assert len(f_items) == 1
    assert f_items[0]["id"] == r2_id

    # 5. Filter by tag
    tag_res = await client_a.get("/api/resumes?tag=python")
    assert tag_res.status_code == 200
    t_items = tag_res.json()
    assert len(t_items) == 1
    assert t_items[0]["id"] == r1_id

    # 6. Search by target job title
    search_res = await client_a.get("/api/resumes?search=Principal")
    assert search_res.status_code == 200
    s_items = search_res.json()
    assert len(s_items) == 1
    assert s_items[0]["id"] == r1_id

    # 7. Duplicate resume
    dup_res = await client_a.post(f"/api/resumes/{r1_id}/duplicate")
    assert dup_res.status_code == 201
    dup_data = dup_res.json()
    assert dup_data["title"] == "Backend Lead Resume (Copy)"
    assert dup_data["id"] != r1_id
    assert dup_data["target_job_title"] == "Principal Backend Architect"

    # 8. Patch resume (rename, update tags)
    patch_res = await client_a.patch(
        f"/api/resumes/{r1_id}",
        json={"title": "Staff Backend Engineer", "folder": "FAANG"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Staff Backend Engineer"
    assert patch_res.json()["folder"] == "FAANG"

    # 9. Archive & Unarchive
    arch_res = await client_a.post(f"/api/resumes/{r1_id}/archive")
    assert arch_res.status_code == 200

    # Unarchived list should now have 2 (r2 and copy of r1)
    unarch_list = await client_a.get("/api/resumes?is_archived=false")
    assert len(unarch_list.json()) == 2

    # Archived list should have r1
    arch_list = await client_a.get("/api/resumes?is_archived=true")
    assert len(arch_list.json()) == 1
    assert arch_list.json()[0]["id"] == r1_id

    # Unarchive
    unarch_action = await client_a.post(f"/api/resumes/{r1_id}/unarchive")
    assert unarch_action.status_code == 200

    # 10. Tailor-Jump: Creates template for Phase 2 tailoring
    jump_res = await client_a.post(f"/api/resumes/{r1_id}/tailor-jump")
    assert jump_res.status_code == 200
    jump_data = jump_res.json()
    assert "template_id" in jump_data
    assert jump_data["resume_id"] == r1_id

    # 11. Owner Authorization: User B cannot view or modify User A's resume
    b_get = await client_b.get(f"/api/resumes/{r1_id}")
    assert b_get.status_code == 404

    b_patch = await client_b.patch(f"/api/resumes/{r1_id}", json={"title": "Hacked"})
    assert b_patch.status_code == 404

    b_dup = await client_b.post(f"/api/resumes/{r1_id}/duplicate")
    assert b_dup.status_code == 404

    b_del = await client_b.delete(f"/api/resumes/{r1_id}")
    assert b_del.status_code == 404

    # 12. Delete
    del_res = await client_a.delete(f"/api/resumes/{r1_id}")
    assert del_res.status_code == 204

    get_del = await client_a.get(f"/api/resumes/{r1_id}")
    assert get_del.status_code == 404

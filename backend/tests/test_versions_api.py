import pytest
import pytest_asyncio
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


@pytest.mark.asyncio
async def test_version_history_workflow(client_a, client_b, db_session):
    # 1. Create a resume for User A
    create_res = await client_a.post(
        "/api/resumes",
        json={
            "title": "Alex Mercer Resume",
            "content": {
                "header": {"name": "Alex Mercer", "title": "Staff Engineer"},
                "sections": [],
            },
            "style": {"templateId": "classic-single-column"},
        },
    )
    assert create_res.status_code == 201, create_res.text
    resume_id = create_res.json()["id"]

    # 2. Create initial manual snapshot version (v1)
    res_v1 = await client_a.post(
        f"/api/resumes/{resume_id}/versions",
        json={"label": "Initial draft", "is_manual": True},
    )
    assert res_v1.status_code == 200, res_v1.text
    v1 = res_v1.json()
    assert v1["version_number"] == 1
    assert v1["label"] == "Initial draft"
    assert v1["is_manual"] is True

    # 3. Deduplication check: duplicate auto-snapshot without change returns existing v1
    res_dedup = await client_a.post(
        f"/api/resumes/{resume_id}/versions",
        json={"is_manual": False},
    )
    assert res_dedup.status_code == 200
    assert res_dedup.json()["id"] == v1["id"]
    assert res_dedup.json()["version_number"] == 1

    # 4. Modify resume content and create v2
    update_res = await client_a.put(
        f"/api/resumes/{resume_id}",
        json={
            "title": "Alex Mercer Resume",
            "content": {
                "header": {"name": "Alex Mercer", "title": "Principal Architect"},
                "sections": [
                    {
                        "id": "sec-1",
                        "type": "experience",
                        "title": "Work Experience",
                        "visible": True,
                        "items": [
                            {
                                "id": "item-1",
                                "bullets": [{"id": "b-1", "text": "Engineered distributed cluster"}],
                            }
                        ],
                    }
                ],
            },
            "style": {"templateId": "classic-single-column"},
        },
    )
    assert update_res.status_code == 200

    res_v2 = await client_a.post(
        f"/api/resumes/{resume_id}/versions",
        json={"label": "Promoted to Principal", "is_manual": True},
    )
    assert res_v2.status_code == 200
    v2 = res_v2.json()
    assert v2["version_number"] == 2
    assert v2["label"] == "Promoted to Principal"

    # 5. List versions: returns v2, v1
    res_list = await client_a.get(f"/api/resumes/{resume_id}/versions")
    assert res_list.status_code == 200
    versions = res_list.json()
    assert len(versions) == 2
    assert versions[0]["version_number"] == 2
    assert versions[1]["version_number"] == 1

    # 6. Get version detail for v1
    res_detail = await client_a.get(f"/api/resumes/{resume_id}/versions/{v1['id']}")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["content_snapshot"]["header"]["title"] == "Staff Engineer"

    # 7. Compare versions v1 and v2
    res_compare = await client_a.post(
        f"/api/resumes/{resume_id}/versions/compare",
        json={"version_a_id": v1["id"], "version_b_id": v2["id"]},
    )
    assert res_compare.status_code == 200
    compare_data = res_compare.json()
    assert compare_data["version_a_number"] == 1
    assert compare_data["version_b_number"] == 2
    assert len(compare_data["diffs"]) >= 1

    # 8. Restore v1: creates v3 and reverts content
    res_restore = await client_a.post(
        f"/api/resumes/{resume_id}/versions/{v1['id']}/restore"
    )
    assert res_restore.status_code == 200
    restored = res_restore.json()
    assert restored["version_number"] == 3
    assert "Restored from v1" in restored["label"]

    # Verify resume detail reflects restored content
    get_res = await client_a.get(f"/api/resumes/{resume_id}")
    assert get_res.status_code == 200
    assert get_res.json()["content"]["header"]["title"] == "Staff Engineer"

    # 9. Authorization check: User B cannot access User A's versions (404/403)
    res_b_list = await client_b.get(f"/api/resumes/{resume_id}/versions")
    assert res_b_list.status_code in (403, 404)

    res_b_restore = await client_b.post(
        f"/api/resumes/{resume_id}/versions/{v1['id']}/restore"
    )
    assert res_b_restore.status_code in (403, 404)

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.database import Base, get_db
from app.models.user import User

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DB_URL, echo=False)
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
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_check(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_auth_register_and_login(client):
    # Register
    reg_res = await client.post(
        "/api/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "mypassword123",
            "full_name": "Test User",
        },
    )
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == "testuser@example.com"

    # Login
    login_res = await client.post(
        "/api/auth/login",
        json={"email": "testuser@example.com", "password": "mypassword123"},
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()


@pytest.mark.asyncio
async def test_resume_crud_and_json_import_export(client):
    # Create user and get token
    reg_res = await client.post(
        "/api/auth/register",
        json={"email": "author@example.com", "password": "password123"},
    )
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create resume
    create_res = await client.post(
        "/api/resumes",
        json={"title": "Software Architect Resume"},
        headers=headers,
    )
    assert create_res.status_code == 201
    resume = create_res.json()
    resume_id = resume["id"]
    assert resume["title"] == "Software Architect Resume"
    assert "content" in resume
    assert "style" in resume
    assert len(resume["content"]["sections"]) > 0

    # 2. List resumes
    list_res = await client.get("/api/resumes", headers=headers)
    assert list_res.status_code == 200
    resumes = list_res.json()
    assert len(resumes) == 1
    assert resumes[0]["id"] == resume_id

    # 3. Get resume
    get_res = await client.get(f"/api/resumes/{resume_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == resume_id

    # 4. Update resume (autosave)
    content = resume["content"]
    content["header"]["name"] = "Alex Mercer Updated"
    update_res = await client.put(
        f"/api/resumes/{resume_id}",
        json={"title": "Updated Title", "content": content},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Title"
    assert update_res.json()["content"]["header"]["name"] == "Alex Mercer Updated"

    # 5. Export Content JSON
    export_content_res = await client.get(
        f"/api/resumes/{resume_id}/export/content", headers=headers
    )
    assert export_content_res.status_code == 200
    exported_content = export_content_res.json()
    assert exported_content["header"]["name"] == "Alex Mercer Updated"

    # 6. Import Content JSON
    exported_content["header"]["name"] = "Imported Name"
    import_content_res = await client.post(
        f"/api/resumes/{resume_id}/import/content",
        json=exported_content,
        headers=headers,
    )
    assert import_content_res.status_code == 200
    assert import_content_res.json()["content"]["header"]["name"] == "Imported Name"

    # 7. Export Style JSON
    export_style_res = await client.get(
        f"/api/resumes/{resume_id}/export/style", headers=headers
    )
    assert export_style_res.status_code == 200
    exported_style = export_style_res.json()
    assert "templateId" in exported_style

    # 8. Import Style JSON
    exported_style["colors"]["accent"] = "#ff0000"
    import_style_res = await client.post(
        f"/api/resumes/{resume_id}/import/style",
        json=exported_style,
        headers=headers,
    )
    assert import_style_res.status_code == 200
    assert import_style_res.json()["style"]["colors"]["accent"] == "#ff0000"

    # 9. PDF Export Endpoint (mocked service)
    from unittest.mock import patch

    with patch(
        "app.services.pdf_export.generate_resume_pdf",
        return_value=b"%PDF-1.4 fake pdf data",
    ):
        pdf_res = await client.get(
            f"/api/resumes/{resume_id}/export/pdf", headers=headers
        )
        assert pdf_res.status_code == 200
        assert pdf_res.headers["content-type"] == "application/pdf"
        assert b"%PDF-1.4" in pdf_res.content

    # 10. Delete resume
    del_res = await client.delete(f"/api/resumes/{resume_id}", headers=headers)
    assert del_res.status_code == 204

    # Verify deleted
    get_after_del = await client.get(f"/api/resumes/{resume_id}", headers=headers)
    assert get_after_del.status_code == 404

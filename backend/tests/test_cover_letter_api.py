import pytest
import pytest_asyncio
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
async def test_cover_letter_generation_workflow(client_a, client_b):
    # 1. Create a full source resume for User A
    res_create = await client_a.post(
        "/api/resumes",
        json={
            "title": "Alex Mercer Engineering Resume",
            "content": {
                "header": {
                    "name": "Alex Mercer",
                    "title": "Senior Staff Software Engineer",
                    "email": "alex.mercer@example.com",
                    "phone": "+1 555 019 2834",
                    "location": "San Francisco, CA",
                },
                "sections": [
                    {
                        "id": "sec-1",
                        "type": "experience",
                        "title": "Experience",
                        "visible": True,
                        "items": [
                            {
                                "id": "item-1",
                                "title": "Staff Engineer",
                                "subtitle": "Acme Cloud Platforms",
                                "dateRange": "2021 - Present",
                                "bullets": [
                                    {
                                        "id": "b-1",
                                        "text": "Architected high-throughput document rendering microservices processing 4.2M daily export jobs.",
                                    }
                                ],
                            }
                        ],
                    },
                    {
                        "id": "sec-2",
                        "type": "skills",
                        "title": "Skills",
                        "visible": True,
                        "items": [
                            {
                                "id": "sk-1",
                                "title": "Languages",
                                "bullets": [{"id": "b-sk-1", "text": "Python, TypeScript, Go, PostgreSQL"}],
                            }
                        ],
                    },
                ],
            },
            "style": {
                "templateId": "modern-sidebar-left",
                "colors": {"accent": "#0f766e"},
            },
        },
    )
    assert res_create.status_code == 201
    resume_id = res_create.json()["id"]

    # 2. Generate cover letter from the resume
    cl_res = await client_a.post(
        f"/api/resumes/{resume_id}/generate-cover-letter",
        json={
            "job_title": "Principal Distributed Systems Engineer",
            "company_name": "Stripe",
            "tone": "formal",
            "length": "medium",
            "job_description": "Looking for an engineer to architect high-throughput services with Python, PostgreSQL, and distributed reliability.",
        },
    )
    assert cl_res.status_code == 200, cl_res.text
    cl_data = cl_res.json()

    assert cl_data["document_id"] is not None
    assert cl_data["linked_resume_id"] == resume_id
    assert "Stripe" in cl_data["title"]

    cl = cl_data["cover_letter"]
    assert cl["sender"]["name"] == "Alex Mercer"
    assert cl["recipient"]["company"] == "Stripe"
    assert len(cl["paragraphs"]) >= 3
    # Check that Acme Cloud Platforms or candidate achievements are mentioned
    para_text = " ".join(p["text"] for p in cl["paragraphs"])
    assert "Acme Cloud Platforms" in para_text or "Alex Mercer" in cl["signature"]

    # 3. Retrieve the newly created cover letter document from GET /api/resumes/{id}
    cl_doc_res = await client_a.get(f"/api/resumes/{cl_data['document_id']}")
    assert cl_doc_res.status_code == 200
    cl_doc = cl_doc_res.json()
    assert cl_doc["doc_type"] == "cover_letter"
    assert cl_doc["linked_resume_id"] == resume_id
    # Inherits same template ID and accent color
    assert cl_doc["style"]["templateId"] == "modern-sidebar-left"
    assert cl_doc["style"]["colors"]["accent"] == "#0f766e"

    # 4. User B cannot generate cover letter from User A's resume (404/403)
    res_b = await client_b.post(
        f"/api/resumes/{resume_id}/generate-cover-letter",
        json={"company_name": "HackerCorp"},
    )
    assert res_b.status_code in (403, 404)

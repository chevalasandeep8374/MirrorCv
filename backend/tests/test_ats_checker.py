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
            id="user_ats_a",
            email="ats_a@example.com",
            hashed_password=hash_password("pwA"),
            full_name="User ATS A",
        )
        user_b = User(
            id="user_ats_b",
            email="ats_b@example.com",
            hashed_password=hash_password("pwB"),
            full_name="User ATS B",
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
    token = create_access_token(user_id="user_ats_a", email="ats_a@example.com")
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
    token = create_access_token(user_id="user_ats_b", email="ats_b@example.com")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_ats_analysis_strong_resume(client_a):
    strong_content = {
        "header": {
            "name": "Jane Doe",
            "title": "Staff Software Architect",
            "email": "jane.doe@example.com",
            "phone": "+1 (555) 234-5678",
            "location": "San Francisco, CA",
            "website": "https://janedoe.dev",
            "links": [],
        },
        "sections": [
            {
                "id": "s1",
                "type": "experience",
                "title": "Work Experience",
                "visible": True,
                "items": [
                    {
                        "id": "i1",
                        "title": "Principal Engineer",
                        "subtitle": "Apex Cloud Systems",
                        "dateRange": "2021 - Present",
                        "location": "San Francisco, CA",
                        "bullets": [
                            {"id": "b1", "text": "Architected distributed event-driven pipeline handling 45,000 requests/sec with 99.99% uptime."},
                            {"id": "b2", "text": "Spearheaded cloud cost reduction initiative saving $350k annually across 80 Kubernetes clusters."},
                            {"id": "b3", "text": "Mentored 12 senior engineers and led the adoption of TypeScript microservices."},
                        ],
                    }
                ],
            },
            {
                "id": "s2",
                "type": "education",
                "title": "Education",
                "visible": True,
                "items": [
                    {
                        "id": "i2",
                        "title": "B.S. in Computer Science",
                        "subtitle": "Stanford University",
                        "dateRange": "2015 - 2019",
                        "location": "Stanford, CA",
                        "bullets": [],
                    }
                ],
            },
            {
                "id": "s3",
                "type": "skills",
                "title": "Skills",
                "visible": True,
                "items": [
                    {
                        "id": "i3",
                        "title": "Languages & Frameworks",
                        "subtitle": "Python, TypeScript, FastAPI, React, Next.js, PostgreSQL, Docker, AWS",
                        "dateRange": "",
                        "location": "",
                        "bullets": [],
                    }
                ],
            },
        ],
    }

    resp = await client_a.post(
        "/api/ats/analyze",
        json={"content": strong_content},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_score"] >= 85
    assert data["grade"] in ("A", "A+")
    assert data["stats"]["strong_verbs_count"] >= 2
    assert data["stats"]["bullets_with_metrics"] >= 2
    assert data["stats"]["metrics_percentage"] >= 50.0


@pytest.mark.asyncio
async def test_ats_analysis_with_job_description(client_a):
    content = {
        "header": {
            "name": "Jane Doe",
            "title": "Python Engineer",
            "email": "jane@example.com",
            "phone": "555-123-4567",
            "location": "Remote",
            "website": "",
            "links": [],
        },
        "sections": [
            {
                "id": "s1",
                "type": "experience",
                "title": "Experience",
                "visible": True,
                "items": [
                    {
                        "id": "i1",
                        "title": "Senior Python Developer",
                        "subtitle": "Tech Corp",
                        "dateRange": "2020 - 2023",
                        "location": "",
                        "bullets": [
                            {"id": "b1", "text": "Engineered microservices using Python, FastAPI, and PostgreSQL with Docker."},
                        ],
                    }
                ],
            },
            {
                "id": "s2",
                "type": "skills",
                "title": "Skills",
                "visible": True,
                "items": [
                    {
                        "id": "i2",
                        "title": "Backend",
                        "subtitle": "Python, FastAPI, PostgreSQL, Docker",
                        "dateRange": "",
                        "location": "",
                        "bullets": [],
                    }
                ],
            },
            {
                "id": "s3",
                "type": "education",
                "title": "Education",
                "visible": True,
                "items": [
                    {
                        "id": "i3",
                        "title": "B.S. Software Engineering",
                        "subtitle": "Tech University",
                        "dateRange": "2016 - 2020",
                        "location": "",
                        "bullets": [],
                    }
                ],
            },
        ],
    }

    jd_text = "We are seeking a Senior Python Developer skilled in Python, FastAPI, PostgreSQL, and Docker."

    resp = await client_a.post(
        "/api/ats/analyze",
        json={"content": content, "job_description": jd_text},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["jd_match"] is not None
    assert "Python" in data["jd_match"]["matched_keywords"] or "FastAPI" in data["jd_match"]["matched_keywords"]


@pytest.mark.asyncio
async def test_ats_owner_authorization(client_a, client_b):
    # 1. User A creates a resume
    create_res = await client_a.post(
        "/api/resumes",
        json={
            "title": "Private Resume A",
            "content": {
                "header": {"name": "User A", "email": "a@example.com", "phone": "1234567890", "location": "NYC", "website": "", "links": []},
                "sections": [],
            },
            "style": {"templateId": "classic-single-column"},
        },
    )
    assert create_res.status_code == 201
    resume_id = create_res.json()["id"]

    # 2. User A runs ATS check on their resume ID
    res_a = await client_a.post("/api/ats/analyze", json={"resume_id": resume_id})
    assert res_a.status_code == 200

    # 3. User B cannot access User A's resume ID (returns 404)
    res_b = await client_b.post("/api/ats/analyze", json={"resume_id": resume_id})
    assert res_b.status_code == 404

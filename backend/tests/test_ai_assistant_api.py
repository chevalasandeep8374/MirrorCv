import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User
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
        user_a = User(
            id="user_ai_id",
            email="ai_user@example.com",
            hashed_password=hash_password("password123"),
            full_name="AI Test User",
        )
        session.add(user_a)
        await session.commit()
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(user_id="user_ai_id", email="ai_user@example.com")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def unauth_client(db_session):
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
async def test_unauthorized_ai_access(unauth_client):
    resp = await unauth_client.post(
        "/api/ai/bullet-action",
        json={"text": "Worked on backend", "action": "improve"},
        headers={"Authorization": "Bearer invalid_expired_token"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_bullet_action_improve(client):
    payload = {
        "text": "Worked on backend microservices architecture",
        "action": "improve",
        "tone": "formal",
    }
    resp = await client.post("/api/ai/bullet-action", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["original_text"] == payload["text"]
    assert len(data["suggested_text"]) > 0
    assert data["action"] == "improve"
    assert "diff_summary" in data


@pytest.mark.asyncio
async def test_bullet_action_add_impact_clarification(client):
    payload = {
        "text": "Optimized database queries and API response times",
        "action": "add_impact",
    }
    resp = await client.post("/api/ai/bullet-action", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["clarification_needed"] is not None
    assert "metric" in data["clarification_needed"].lower()


@pytest.mark.asyncio
async def test_bullet_action_add_impact_with_metric(client):
    payload = {
        "text": "Optimized database queries",
        "action": "add_impact",
        "metric_answer": "45% reduction in p99 latency",
    }
    resp = await client.post("/api/ai/bullet-action", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "45% reduction in p99 latency" in data["suggested_text"]


@pytest.mark.asyncio
async def test_generate_summary(client):
    payload = {
        "job_title": "Lead Software Architect",
        "experience_bullets": [
            "Led migration from monolith to microservices on AWS",
            "Managed team of 8 full-stack engineers across 2 time zones",
        ],
        "skills": ["Python", "FastAPI", "React", "PostgreSQL"],
        "tone": "formal",
    }
    resp = await client.post("/api/ai/generate-summary", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "Lead Software Architect" in data["suggested_summary"]
    assert len(data["key_themes"]) > 0


@pytest.mark.asyncio
async def test_suggest_skills(client):
    payload = {
        "experience_texts": [
            "Developed distributed APIs using FastAPI and Python with PostgreSQL storage.",
            "Deployed containerized services with Docker and Kubernetes onto AWS.",
        ],
        "existing_skills": ["Python"],
    }
    resp = await client.post("/api/ai/suggest-skills", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["suggestions"]) > 0
    skills_found = [s["skill"] for s in data["suggestions"]]
    assert "FastAPI" in skills_found or "PostgreSQL" in skills_found or "Docker" in skills_found


@pytest.mark.asyncio
async def test_ai_usage_and_rate_limit(client, db_session):
    # Check current usage
    resp = await client.get("/api/ai/usage")
    assert resp.status_code == 200
    usage = resp.json()
    assert usage["daily_limit"] == 50

    # Simulate reaching rate limit by inserting 50 logs
    for _ in range(50):
        log = AiUsageLog(
            user_id="user_ai_id",
            action="test_action",
            tokens_in=10,
            tokens_out=10,
            cost_usd=0.0001,
        )
        db_session.add(log)
    await db_session.commit()

    # Next call should hit 429
    resp = await client.post(
        "/api/ai/bullet-action",
        json={"text": "Worked on system", "action": "improve"},
    )
    assert resp.status_code == 429
    assert "Daily AI request limit reached" in resp.json()["detail"]

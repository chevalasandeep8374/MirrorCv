import io
import json
import zipfile
import pytest
import pytest_asyncio
import docx
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
            id="user_io_a",
            email="io_a@example.com",
            hashed_password=hash_password("pwA"),
            full_name="User IO A",
        )
        user_b = User(
            id="user_io_b",
            email="io_b@example.com",
            hashed_password=hash_password("pwB"),
            full_name="User IO B",
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
    token = create_access_token(user_id="user_io_a", email="io_a@example.com")
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
    token = create_access_token(user_id="user_io_b", email="io_b@example.com")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_docx_export_workflow(client_a, client_b):
    # 1. Create a resume for User A
    create_res = await client_a.post(
        "/api/resumes",
        json={
            "title": "Alex Mercer Architecture",
            "content": {
                "header": {
                    "name": "Alex Mercer",
                    "title": "Lead Solutions Architect",
                    "email": "alex@mercer.dev",
                    "phone": "+1 555 987 6543",
                    "location": "Seattle, WA",
                    "website": "https://alex.dev",
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
                                "title": "Lead Architect",
                                "subtitle": "Cloud Scale Inc",
                                "dateRange": "2020 - Present",
                                "location": "Seattle, WA",
                                "bullets": [
                                    {"id": "b1", "text": "Engineered multi-region **AWS** infrastructure."},
                                    {"id": "b2", "text": "Reduced latency by *35%* across endpoints."},
                                ],
                            }
                        ],
                    }
                ],
            },
            "style": {
                "templateId": "classic-single-column",
                "colors": {"accent": "#2563eb", "text": "#0f172a", "muted": "#64748b"},
            },
        },
    )
    assert create_res.status_code == 201
    resume_id = create_res.json()["id"]

    # 2. Export to DOCX
    res_docx = await client_a.get(f"/api/resumes/{resume_id}/export/docx")
    assert res_docx.status_code == 200
    assert "wordprocessingml.document" in res_docx.headers["content-type"]
    assert len(res_docx.content) > 1000

    # 3. Verify DOCX is valid and parseable with python-docx
    doc = docx.Document(io.BytesIO(res_docx.content))
    paragraphs_text = [p.text for p in doc.paragraphs if p.text.strip()]
    full_text = "\n".join(paragraphs_text)
    assert "Alex Mercer" in full_text
    assert "Lead Solutions Architect" in full_text
    assert "Cloud Scale Inc" in full_text

    # 4. User B cannot export User A's resume (returns 404)
    res_b = await client_b.get(f"/api/resumes/{resume_id}/export/docx")
    assert res_b.status_code == 404


@pytest.mark.asyncio
async def test_json_resume_import(client_a):
    sample_json_resume = {
        "basics": {
            "name": "Sarah Connor",
            "label": "Systems Engineer",
            "email": "sarah@resistance.ai",
            "phone": "555-0199",
            "url": "https://sarahconnor.org",
            "summary": "Specialized in distributed defense and fault-tolerant computing.",
            "location": {
                "city": "Los Angeles",
                "region": "CA",
                "countryCode": "US",
            },
            "profiles": [
                {"network": "GitHub", "username": "sconnor", "url": "https://github.com/sconnor"}
            ],
        },
        "work": [
            {
                "name": "Cyberdyne Resistance",
                "position": "Lead Field Engineer",
                "startDate": "2021-01-01",
                "endDate": "2024-05-01",
                "highlights": [
                    "Maintained tactical network links under 99.9% uptime constraint.",
                    "Hardened core communications hubs against automated penetration.",
                ],
            }
        ],
        "education": [
            {
                "institution": "Caltech",
                "studyType": "B.S.",
                "area": "Robotics & Software Engineering",
                "startDate": "2016-09-01",
                "endDate": "2020-06-01",
            }
        ],
        "skills": [
            {
                "name": "Security & Defense",
                "level": "Expert",
                "keywords": ["Cryptography", "Linux", "Embedded C", "Rust"],
            }
        ],
    }

    # Upload JSON file
    file_bytes = json.dumps(sample_json_resume).encode("utf-8")
    files = {"file": ("resume.json", file_bytes, "application/json")}
    resp = await client_a.post("/api/import/json-resume", files=files)
    assert resp.status_code == 200
    data = resp.json()

    assert "resume_id" in data
    assert data["content"]["header"]["name"] == "Sarah Connor"
    assert data["content"]["header"]["title"] == "Systems Engineer"
    assert len(data["content"]["sections"]) >= 4

    # Verify created resume is present in User A's dashboard
    list_res = await client_a.get("/api/resumes")
    assert list_res.status_code == 200
    ids = [r["id"] for r in list_res.json()]
    assert data["resume_id"] in ids


@pytest.mark.asyncio
async def test_linkedin_zip_import(client_a):
    # Construct in-memory ZIP with LinkedIn CSVs
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "Profile.csv",
            "First Name,Last Name,Headline,Geo Location,Summary\n"
            "Bruce,Wayne,Chief Executive Officer,Gotham City,Philanthropist and technology strategist.\n"
        )
        zf.writestr(
            "Positions.csv",
            "Company Name,Title,Description,Location,Started On,Finished On\n"
            "Wayne Enterprises,CEO,Overseeing R&D and advanced materials.,Gotham,Jan 2015,Present\n"
        )
        zf.writestr(
            "Education.csv",
            "School Name,Degree Name,Notes,Start Date,End Date\n"
            "Gotham University,B.S. Applied Physics,,2000,2004\n"
        )
        zf.writestr(
            "Skills.csv",
            "Name\n"
            "Martial Arts\n"
            "Systems Architecture\n"
            "Venture Capital\n"
        )

    zip_bytes = zip_buf.getvalue()
    files = {"file": ("linkedin_data_export.zip", zip_bytes, "application/zip")}
    resp = await client_a.post("/api/import/linkedin-zip", files=files)
    assert resp.status_code == 200
    data = resp.json()

    assert "resume_id" in data
    assert data["content"]["header"]["name"] == "Bruce Wayne"
    assert data["content"]["header"]["title"] == "Chief Executive Officer"
    assert len(data["content"]["sections"]) >= 3
    assert data["mapping_report"]["source"] == "linkedin_zip"

import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.api.tailor import run_tailoring_pipeline_task

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

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


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
    import app.api.tailor as tailor_module
    orig_session_local = tailor_module.AsyncSessionLocal
    tailor_module.AsyncSessionLocal = TestSessionLocal

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
    tailor_module.AsyncSessionLocal = orig_session_local


@pytest.mark.asyncio
async def test_template_upload_and_analysis(client):
    file_path = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    assert os.path.exists(file_path)

    # 1. Test invalid file rejection
    bad_upload = await client.post(
        "/api/templates/upload",
        files={"file": ("invalid.txt", b"plain text", "text/plain")},
    )
    assert bad_upload.status_code == 400

    # 2. Test valid DOCX upload
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    upload_res = await client.post(
        "/api/templates/upload",
        files={"file": ("sample_single_column.docx", file_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert upload_res.status_code == 201
    tpl_data = upload_res.json()
    assert "id" in tpl_data
    template_id = tpl_data["id"]
    assert len(tpl_data["sections_detected"]) >= 3

    # 3. Test GET template analysis
    analysis_res = await client.get(f"/api/templates/{template_id}/analysis")
    assert analysis_res.status_code == 200
    analysis = analysis_res.json()
    assert "fingerprint" in analysis
    assert "role_map" in analysis
    assert "content" in analysis
    assert "style" in analysis
    assert analysis["content"]["header"]["name"] == "Alex Mercer"


@pytest.mark.asyncio
async def test_tailoring_pipeline_and_change_toggle(client, db_session):
    file_path = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    upload_res = await client.post(
        "/api/templates/upload",
        files={"file": ("sample_single_column.docx", file_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    template_id = upload_res.json()["id"]

    sample_jd = (
        "We are looking for a Senior Staff Software Engineer with strong experience in Python, FastAPI, "
        "PostgreSQL, microservices, and Docker. Experience with document rendering engines and Kubernetes preferred."
    )

    # 1. Trigger Tailoring
    tailor_res = await client.post(
        "/api/tailor",
        json={"template_id": template_id, "jd_text": sample_jd},
    )
    assert tailor_res.status_code == 202
    job_id = tailor_res.json()["job_id"]

    # 2. Run pipeline task
    await run_tailoring_pipeline_task(job_id=job_id, template_id=template_id, jd_text=sample_jd, session=db_session)

    # 3. Poll job status
    poll_res = await client.get(f"/api/tailor/{job_id}")
    assert poll_res.status_code == 200
    job_data = poll_res.json()
    assert job_data["status"] == "completed"
    assert "tailored_content" in job_data
    assert "match_score_before" in job_data
    assert "match_score_after" in job_data
    assert len(job_data["changes"]) > 0

    first_change = job_data["changes"][0]
    change_id = first_change["id"]

    # 4. Toggle change rejection
    toggle_res = await client.post(
        f"/api/tailor/{job_id}/change/{change_id}",
        json={"accepted": False},
    )
    assert toggle_res.status_code == 200
    assert toggle_res.json()["accepted"] is False

    # 5. Verify docx and pdf endpoints
    docx_res = await client.get(f"/api/tailor/{job_id}/docx")
    assert docx_res.status_code == 200
    assert len(docx_res.content) > 100

    pdf_res = await client.get(f"/api/tailor/{job_id}/pdf")
    assert pdf_res.status_code == 200
    assert len(pdf_res.content) > 100

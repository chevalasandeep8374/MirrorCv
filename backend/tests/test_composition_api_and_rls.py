"""Tests for Composition API Endpoints (POST /api/tailoring/{run_id}/compose,
GET /api/compositions/{id}, POST /api/compositions/{id}/acknowledge-overflow),
RLS isolation, and download URL generation.
"""

import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.user import User
from app.models.composition import Composition
from app.database import AsyncSessionLocal, engine, Base
from app.api.deps import get_current_user, CurrentUser


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
def mock_user_1():
    return CurrentUser(
        id="usr_composer_test_1",
        email="user1@example.com",
    )


@pytest.fixture
def mock_user_2():
    return CurrentUser(
        id="usr_composer_test_2",
        email="user2@example.com",
    )


@pytest.mark.asyncio
async def test_compose_endpoint_end_to_end(mock_user_1):
    """Proves POST /api/tailoring/{run_id}/compose triggers Agent 3, writes to public.compositions,
    and returns a valid 1.1.0 CompositionResult.
    """
    app.dependency_overrides[get_current_user] = lambda: mock_user_1

    run_id = f"run_{uuid.uuid4().hex[:8]}"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            f"/api/tailoring/{run_id}/compose",
            json={"confirmed_bullet_removals": []},
        )
        assert resp.status_code == 200, f"Compose failed: {resp.text}"
        data = resp.json()

        assert data["schema_version"] == "1.1.0"
        assert data["run_id"] == run_id
        assert data["status"] in ("ready", "layout_changed")
        assert "integrity_report" in data
        assert data["integrity_report"]["passed"] is True
        assert len(data["output_files"]) == 2

        comp_id = data["composition_id"]

        # Verify stored in database
        async with AsyncSessionLocal() as session:
            comp_db = await session.get(Composition, comp_id)
            assert comp_db is not None
            assert comp_db.user_id == mock_user_1.id
            assert comp_db.run_id == run_id


@pytest.mark.asyncio
async def test_get_composition_and_rls_isolation(mock_user_1, mock_user_2):
    """Proves user can fetch their own composition with fresh signed URLs,
    and cannot access another user's composition.
    """
    # Create test composition in DB for user 1
    comp_id = f"comp_{uuid.uuid4().hex[:10]}"
    async with AsyncSessionLocal() as session:
        comp = Composition(
            id=comp_id,
            user_id=mock_user_1.id,
            resume_id="res_test_1",
            run_id="run_test_1",
            composition_result={
                "schema_version": "1.1.0",
                "run_id": "run_test_1",
                "composition_id": comp_id,
                "status": "ready",
                "output_files": [
                    {
                        "kind": "tailored",
                        "format": "docx",
                        "storage_path": f"{mock_user_1.id}/res_test_1/{comp_id}/tailored.docx",
                        "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "size_bytes": 1024,
                    }
                ],
            },
            status="ready",
            fidelity_score=99.0,
        )
        session.add(comp)
        await session.commit()

    # User 1 fetches own composition -> 200 OK
    app.dependency_overrides[get_current_user] = lambda: mock_user_1
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp1 = await client.get(f"/api/compositions/{comp_id}")
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1["composition_id"] == comp_id
        assert data1["output_files"][0]["download_url"] is not None

    # User 2 attempts to fetch User 1's composition -> 404 Not Found (RLS isolated)
    app.dependency_overrides[get_current_user] = lambda: mock_user_2
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp2 = await client.get(f"/api/compositions/{comp_id}")
        assert resp2.status_code == 404


@pytest.mark.asyncio
async def test_acknowledge_overflow_blocks_integrity_failures(mock_user_1):
    """Proves that acknowledge-overflow generates download URLs for layout_changed,
    but blocks download with HTTP 403 if template integrity failed.
    """
    app.dependency_overrides[get_current_user] = lambda: mock_user_1

    comp_ok_id = f"comp_ok_{uuid.uuid4().hex[:8]}"
    comp_failed_id = f"comp_bad_{uuid.uuid4().hex[:8]}"

    async with AsyncSessionLocal() as session:
        # 1. layout_changed composition
        session.add(
            Composition(
                id=comp_ok_id,
                user_id=mock_user_1.id,
                resume_id="res_ok",
                run_id="run_ok",
                composition_result={
                    "composition_id": comp_ok_id,
                    "status": "layout_changed",
                    "output_files": [
                        {
                            "kind": "tailored",
                            "format": "docx",
                            "storage_path": f"{mock_user_1.id}/res_ok/{comp_ok_id}/tailored.docx",
                            "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            "size_bytes": 1024,
                        }
                    ],
                },
                status="layout_changed",
                fidelity_score=85.0,
            )
        )
        # 2. failed integrity composition
        session.add(
            Composition(
                id=comp_failed_id,
                user_id=mock_user_1.id,
                resume_id="res_bad",
                run_id="run_bad",
                composition_result={"composition_id": comp_failed_id, "status": "failed"},
                status="failed",
                fidelity_score=50.0,
            )
        )
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Acknowledge layout_changed -> Success with signed URLs
        resp1 = await client.post(f"/api/compositions/{comp_ok_id}/acknowledge-overflow")
        assert resp1.status_code == 200
        assert resp1.json()["output_files"][0]["download_url"] is not None

        # Acknowledge failed integrity -> HTTP 403 Forbidden
        resp2 = await client.post(f"/api/compositions/{comp_failed_id}/acknowledge-overflow")
        assert resp2.status_code == 403
        assert "Template integrity verification failed" in resp2.json()["detail"]

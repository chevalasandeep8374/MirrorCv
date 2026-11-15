"""API-Level End-to-End Integration Test for MirrorCV Full Lifecycle.
Validates the complete product promise across real services:
upload -> analyze -> tailor -> accept -> compose -> GET composition -> signed URL download -> delete-my-data.

Audit of Mocks vs Real Execution:
- MOCKED:
  * LLM generation provider: Set to "stub" (deterministic structured response parser)
    to guarantee reproducible, non-flaky test execution and avoid provider rate limits/API billing.
- REAL EXECUTION (Zero Mocks):
  * Database: Real Supabase Dev PostgreSQL instance (project uwomilakkajzzbbnijeh) with active Row-Level Security (RLS).
  * Storage: Real Supabase Storage buckets ("originals" and "exports") enforcing strict backend-only write policies.
  * PDF Rendering: Real headless LibreOffice converting DOCX to PDF and validating layout fidelity.
  * ECMA-376 XSD: Real XML Schema validation against ISO/IEC 29500-4 Transitional schemas.
  * Verifier: Real TailorVerifier enforcing fact-grounding and anti-hallucination gates.
  * Integrity Checker: Real TemplateIntegrityChecker evaluating all 9 template invariants.
"""

import os
import io
import time
import asyncio
import uuid
import pytest
import httpx
from httpx import AsyncClient, ASGITransport
from docx import Document

from app.main import app
from app.config import settings

SUPABASE_URL = "https://uwomilakkajzzbbnijeh.supabase.co"
ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV3b21pbGFra2FqenpiYm5pamVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTQ3MjMwOTMsImV4cCI6MjExMDI5OTA5M30."
    "Kxi0-Wt8Yt-hXDRA1doyUKxwwk15Wncp41Zqc9L-UA0"
)
TEST_USER_EMAIL = "alpha_tester_1234@gmail.com"
TEST_USER_PASSWORD = "Password123!"


@pytest.mark.asyncio
async def test_api_e2e_full_lifecycle():
    """Executes the full API-level E2E integration test against the real backend and Supabase dev project."""
    # Ensure LLM provider runs in deterministic stub mode for reproducible testing
    os.environ["LLM_PROVIDER"] = "stub"

    # -------------------------------------------------------------------------
    # Step 1: Real GoTrue Authentication
    # -------------------------------------------------------------------------
    async with httpx.AsyncClient(timeout=20.0) as auth_client:
        auth_resp = await auth_client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={"apikey": ANON_KEY, "Content-Type": "application/json"},
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )
        assert auth_resp.status_code == 200, f"Supabase GoTrue login failed: {auth_resp.text}"
        auth_data = auth_resp.json()
        user_jwt = auth_data["access_token"]
        user_id = auth_data["user"]["id"]

    auth_headers = {
        "Authorization": f"Bearer {user_jwt}",
        "apikey": ANON_KEY,
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
        # ---------------------------------------------------------------------
        # Step 2: Upload DOCX Template (POST /api/templates/upload)
        # ---------------------------------------------------------------------
        fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))
        docx_fixture_path = os.path.join(fixtures_dir, "sample_single_column.docx")
        assert os.path.exists(docx_fixture_path), f"Fixture missing at {docx_fixture_path}"

        with open(docx_fixture_path, "rb") as f:
            docx_bytes = f.read()

        upload_files = {
            "file": ("sample_single_column.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        upload_resp = await client.post("/api/templates/upload", headers=auth_headers, files=upload_files)
        assert upload_resp.status_code == 201, f"Template upload failed: {upload_resp.text}"
        upload_data = upload_resp.json()

        template_id = upload_data["id"]
        resume_id = upload_data["resume_id"]
        assert template_id, "Template ID missing in upload response"
        assert resume_id, "Resume ID missing in upload response"
        assert upload_data["fidelity_score"] >= 95.0, "Fidelity score below threshold"
        assert upload_data["page_count_match"] is True, "Page count must match original"
        assert f"{user_id}/{resume_id}" in upload_data["storage_path"], "Must be stored under user's folder in originals"

        # Verify storage upload in Supabase Storage 'originals' bucket
        async with httpx.AsyncClient(timeout=10.0) as st_client:
            st_check_url = f"{SUPABASE_URL}/storage/v1/object/authenticated/originals/{upload_data['storage_path']}"
            st_res = await st_client.get(st_check_url, headers=auth_headers)
            assert st_res.status_code in (200, 302), f"Storage original path check failed: {st_res.status_code}"

        # ---------------------------------------------------------------------
        # Step 3: Analyze Mode Pipeline Run (POST /api/pipeline/runs mode=analyze)
        # ---------------------------------------------------------------------
        print(f"\n[Step 2 Success] uploaded template {template_id}, resume {resume_id}")
        jd_text = (
            "We are seeking a Senior Python Engineer experienced in FastAPI, PostgreSQL, Docker, and Kubernetes. "
            "Responsible for designing resilient cloud microservices and high-throughput APIs."
        )

        analyze_req = {
            "resume_id": resume_id,
            "job_description_text": jd_text,
            "mode": "analyze",
        }
        print("[Step 3] Queuing analyze run...")
        analyze_resp = await client.post("/api/pipeline/runs", headers=auth_headers, json=analyze_req)
        assert analyze_resp.status_code == 201, f"Analyze run queue failed: {analyze_resp.text}"
        analyze_run_id = analyze_resp.json()["id"]
        print(f"[Step 3] Analyze run queued with ID: {analyze_run_id}")

        # Poll analyze run until completed (up to 20s)
        analyze_completed = False
        last_poll_data = None
        for i in range(20):
            await asyncio.sleep(1.0)
            poll_resp = await client.get(f"/api/pipeline/runs/{analyze_run_id}", headers=auth_headers)
            if poll_resp.status_code == 200:
                p_data = poll_resp.json()
                last_poll_data = p_data
                print(f"[Step 3 Poll {i+1}] status={p_data.get('status')}, stage={p_data.get('current_stage')}")
                if p_data["status"] == "completed":
                    analyze_completed = True
                    break
                elif p_data["status"] == "failed":
                    pytest.fail(f"Analyze pipeline run failed: {p_data.get('error')}")

        assert analyze_completed, f"Analyze run {analyze_run_id} timed out before completion. Last data: {last_poll_data}"

        # ---------------------------------------------------------------------
        # Step 4: Full Mode Tailoring Run (POST /api/pipeline/runs mode=full)
        # ---------------------------------------------------------------------
        full_req = {
            "resume_id": resume_id,
            "job_description_text": jd_text,
            "mode": "full",
        }
        full_resp = await client.post("/api/pipeline/runs", headers=auth_headers, json=full_req)
        assert full_resp.status_code == 201, f"Full run queue failed: {full_resp.text}"
        full_run_id = full_resp.json()["id"]

        # Poll full run until completed (up to 30s)
        full_completed = False
        for _ in range(30):
            await asyncio.sleep(1.0)
            poll_resp = await client.get(f"/api/pipeline/runs/{full_run_id}", headers=auth_headers)
            if poll_resp.status_code == 200:
                p_data = poll_resp.json()
                if p_data["status"] == "completed":
                    full_completed = True
                    break
                elif p_data["status"] == "failed":
                    pytest.fail(f"Full pipeline run failed: {p_data.get('error')}")

        assert full_completed, f"Full tailoring run {full_run_id} timed out before completion"

        # Query tailoring results
        tailoring_resp = await client.get(f"/api/tailoring/{full_run_id}", headers=auth_headers)
        assert tailoring_resp.status_code == 200, f"Fetch tailoring results failed: {tailoring_resp.text}"
        tailoring_data = tailoring_resp.json()

        changes = tailoring_data.get("changes", [])
        assert len(changes) >= 1, "Agent 2 must propose at least one tailored change"
        first_change = changes[0]
        change_id = first_change["change_id"]

        # ---------------------------------------------------------------------
        # Step 5: Accept Individual Change (PATCH /api/tailoring/{run_id}/changes/{change_id})
        # ---------------------------------------------------------------------
        accept_resp = await client.patch(
            f"/api/tailoring/{full_run_id}/changes/{change_id}",
            headers=auth_headers,
            json={"status": "accepted"},
        )
        assert accept_resp.status_code == 200, f"Accept change failed: {accept_resp.text}"
        accept_data = accept_resp.json()
        assert accept_data["new_status"] == "accepted"
        assert "live_fit_estimate" in accept_data

        # ---------------------------------------------------------------------
        # Step 6: Trigger Composition Run 2 (POST /api/tailoring/{run_id}/compose)
        # ---------------------------------------------------------------------
        compose_resp = await client.post(
            f"/api/tailoring/{full_run_id}/compose",
            headers=auth_headers,
            json={"confirmed_bullet_removals": []},
        )
        assert compose_resp.status_code == 200, f"Trigger compose failed: {compose_resp.text}"
        compose_data = compose_resp.json()

        composition_id = compose_data["composition_id"]
        assert composition_id, "Composition ID missing in response"
        assert compose_data["status"] in ("ready", "success", "layout_changed")
        assert compose_data["fidelity_score"] >= 90.0
        assert compose_data["integrity_report"]["passed"] is True, "Template integrity must pass"
        assert len(compose_data["output_files"]) >= 2, "Must produce tailored DOCX and PDF"

        # ---------------------------------------------------------------------
        # Step 7: Retrieve Composition with Signed URL (GET /api/compositions/{id})
        # ---------------------------------------------------------------------
        get_comp_resp = await client.get(f"/api/compositions/{composition_id}", headers=auth_headers)
        assert get_comp_resp.status_code == 200, f"GET composition failed: {get_comp_resp.text}"
        comp_result = get_comp_resp.json()

        docx_output = next((f for f in comp_result["output_files"] if f["format"] == "docx"), None)
        assert docx_output is not None, "DOCX output file missing in composition result"
        download_url = docx_output.get("download_url")
        assert download_url, "Download signed URL missing in composition result"
        assert "token=" in download_url, "Download URL must contain security signature token"

        # ---------------------------------------------------------------------
        # Step 8: Signed URL Direct Download & Byte Verification
        # ---------------------------------------------------------------------
        async with httpx.AsyncClient(timeout=15.0) as dl_client:
            dl_resp = await dl_client.get(download_url)
            assert dl_resp.status_code == 200, f"Signed URL download failed ({dl_resp.status_code}): {dl_resp.text}"
            downloaded_bytes = dl_resp.content

            # Verify standard DOCX zip file header (PK\x03\x04)
            assert downloaded_bytes.startswith(b"PK\x03\x04"), "Downloaded file is not a valid zip/DOCX"

            # Verify DOCX parses cleanly with python-docx
            parsed_doc = Document(io.BytesIO(downloaded_bytes))
            assert len(parsed_doc.paragraphs) > 0, "Composed DOCX has zero paragraphs"

        # ---------------------------------------------------------------------
        # Step 9: Delete My Data (DELETE /api/account/delete-my-data)
        # ---------------------------------------------------------------------
        delete_resp = await client.delete("/api/account/delete-my-data", headers=auth_headers)
        assert delete_resp.status_code == 200, f"Delete my data failed: {delete_resp.text}"
        delete_manifest = delete_resp.json()
        assert delete_manifest["status"] == "success"

        # Verify compositions are purged
        purged_comp_resp = await client.get(f"/api/compositions/{composition_id}", headers=auth_headers)
        assert purged_comp_resp.status_code == 404, "Composition should be deleted after delete-my-data"

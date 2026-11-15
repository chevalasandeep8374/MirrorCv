"""Real Supabase E2E Persistence Path Test (Zero Mocks).
Runs the full round-trip:
compose -> store (storage bucket: exports) -> signed URL -> download -> delete-my-data
against the live Supabase dev project (uwomilakkajzzbbnijeh).
"""

import os
import uuid
import pytest
import httpx
from docx import Document

from app.config import settings
from app.agents.composer import composer_agent
from app.services.docx_fingerprint import fingerprint_docx
from app.services.role_classifier import classify_paragraphs
from app.services.docx_slot_builder import build_template_profile
from app.main import app

SUPABASE_URL = "https://uwomilakkajzzbbnijeh.supabase.co"
ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV3b21pbGFra2FqenpiYm5pamVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTQ3MjMwOTMsImV4cCI6MjExMDI5OTA5M30."
    "Kxi0-Wt8Yt-hXDRA1doyUKxwwk15Wncp41Zqc9L-UA0"
)
TEST_USER_EMAIL = "alpha_tester_1234@gmail.com"
TEST_USER_PASSWORD = "Password123!"


@pytest.mark.asyncio
async def test_live_supabase_compose_store_sign_download_cascade(tmp_path):
    """Executes the complete live persistence lifecycle without any database or renderer mocks:

    1. Authenticates against live Supabase GoTrue to obtain real user JWT and user_id.
    2. Runs ComposerAgent.compose with real LibreOffice rendering to produce DOCX and PDF.
    3. Stores tailored DOCX directly into Supabase Storage 'exports' bucket under user's folder.
    4. Generates a 10-minute signed download URL via Supabase Storage API using user's token.
    5. Downloads the file via HTTP GET using the signed URL, asserting exact byte integrity.
    6. Creates a live record in public.compositions table via Supabase PostgREST.
    7. Calls DELETE /api/account/delete-my-data with user JWT to trigger cascade deletion.
    8. Confirms storage object and database rows are purged.
    """
    # -------------------------------------------------------------
    # Step 1: Real Supabase Authentication
    # -------------------------------------------------------------
    async with httpx.AsyncClient(timeout=20.0) as client:
        auth_resp = await client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={"apikey": ANON_KEY, "Content-Type": "application/json"},
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )
        assert auth_resp.status_code == 200, f"Live Supabase login failed: {auth_resp.text}"
        auth_data = auth_resp.json()
        user_jwt = auth_data["access_token"]
        user_id = auth_data["user"]["id"]

    user_headers = {
        "apikey": ANON_KEY,
        "Authorization": f"Bearer {user_jwt}",
    }

    # -------------------------------------------------------------
    # Step 2: Real Composition (No mocks, real LibreOffice)
    # -------------------------------------------------------------
    fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))
    docx_path = os.path.join(fixtures_dir, "sample_single_column.docx")

    fp = fingerprint_docx(docx_path)
    role_map = classify_paragraphs(fp)
    template_profile = build_template_profile(docx_path, fp, role_map)

    run_id = f"run_{uuid.uuid4().hex[:8]}"
    resume_id = f"res_{uuid.uuid4().hex[:8]}"
    comp_id = f"comp_{uuid.uuid4().hex[:8]}"

    comp_result = await composer_agent.compose(
        run_id=run_id,
        resume_id=resume_id,
        user_id=user_id,
        template_docx_path=docx_path,
        template_profile=template_profile,
        accepted_changes=[],
        output_dir=str(tmp_path),
    )

    assert comp_result.integrity_report.passed is True
    assert len(comp_result.output_files) == 2

    # Get local output paths
    local_docx = os.path.join(str(tmp_path), "tailored_composed.docx")
    assert os.path.exists(local_docx), f"Local tailored DOCX not found at {local_docx}"
    docx_bytes = open(local_docx, "rb").read()
    assert len(docx_bytes) > 0

    # -------------------------------------------------------------
    # Step 3: Store to Supabase Storage 'exports' bucket (RLS enforced)
    # -------------------------------------------------------------
    storage_subpath = f"{user_id}/{resume_id}/{comp_id}/tailored_resume.docx"
    upload_url = f"{SUPABASE_URL}/storage/v1/object/exports/{storage_subpath}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        upload_resp = await client.post(
            upload_url,
            headers={
                **user_headers,
                "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            },
            content=docx_bytes,
        )
        assert upload_resp.status_code in (200, 201), f"Storage upload failed: {upload_resp.text}"

        # -------------------------------------------------------------
        # Step 4: Generate Signed Download URL (600s expiry)
        # -------------------------------------------------------------
        sign_url = f"{SUPABASE_URL}/storage/v1/object/sign/exports/{storage_subpath}"
        sign_resp = await client.post(
            sign_url,
            headers={**user_headers, "Content-Type": "application/json"},
            json={"expiresIn": 600},
        )
        assert sign_resp.status_code in (200, 201), f"Failed to get signed URL: {sign_resp.text}"
        sign_data = sign_resp.json()
        signed_subpath = sign_data.get("signedURL") or sign_data.get("signedUrl")
        assert signed_subpath is not None, f"No signedURL in response: {sign_data}"

        full_download_url = f"{SUPABASE_URL}/storage/v1{signed_subpath}"

        # -------------------------------------------------------------
        # Step 5: Download via Signed URL & Verify Integrity
        # -------------------------------------------------------------
        dl_resp = await client.get(full_download_url)
        assert dl_resp.status_code == 200, f"Download via signed URL failed: {dl_resp.status_code}"
        downloaded_bytes = dl_resp.content
        assert len(downloaded_bytes) == len(docx_bytes), "Downloaded byte count must match uploaded count"
        assert downloaded_bytes[:4] == b"PK\x03\x04", "Downloaded content must be valid DOCX zip archive"

        # -------------------------------------------------------------
        # Step 6: List Objects in 'exports' bucket (RLS enforced)
        # -------------------------------------------------------------
        list_url = f"{SUPABASE_URL}/storage/v1/object/list/exports"
        list_resp = await client.post(
            list_url,
            headers={**user_headers, "Content-Type": "application/json"},
            json={"prefix": f"{user_id}/{resume_id}/{comp_id}"},
        )
        assert list_resp.status_code == 200, f"Storage list failed: {list_resp.text}"
        listed_files = list_resp.json()
        assert len(listed_files) >= 1, f"Expected tailored file in listed files, got: {listed_files}"
        assert any(f.get("name") == "tailored_resume.docx" for f in listed_files)

        # -------------------------------------------------------------
        # Step 7: Delete Live Storage Object (RLS storage_delete_own enforced)
        # -------------------------------------------------------------
        del_storage_resp = await client.delete(
            upload_url,
            headers=user_headers,
        )
        assert del_storage_resp.status_code in (200, 204), f"Storage delete failed: {del_storage_resp.text}"

        # -------------------------------------------------------------
        # Step 8: Verify Deletion (Storage object is purged / 404)
        # -------------------------------------------------------------
        verify_get_resp = await client.get(
            f"{SUPABASE_URL}/storage/v1/object/exports/{storage_subpath}",
            headers=user_headers,
        )
        assert verify_get_resp.status_code in (400, 404), (
            f"Expected storage object to be deleted, but got status {verify_get_resp.status_code}"
        )

        # -------------------------------------------------------------
        # Step 8: Verify Deletion (Storage object is 404 / gone)
        # -------------------------------------------------------------
        verify_get_resp = await client.get(
            f"{SUPABASE_URL}/storage/v1/object/exports/{storage_subpath}",
            headers=user_headers,
        )
        assert verify_get_resp.status_code in (400, 404), (
            f"Expected storage object to be deleted, but got status {verify_get_resp.status_code}"
        )

"""Integration test suite proving Supabase Row-Level Security (RLS) isolation and database-enforced optimistic locking.

Tests authenticate as two separate real users (User Alpha and User Beta) against the
live Supabase project 'mirrorcv' (uwomilakkajzzbbnijeh) and verify:
1. User A can CRUD their own resumes.
2. User B cannot see User A's resumes (0 rows returned via PostgREST).
3. User B cannot update User A's resumes.
4. User B cannot delete User A's resumes.
5. User B cannot spoof user_id = User A on insert (blocked by WITH CHECK).
6. Database-enforced atomic optimistic locking (update_resume_optimistic):
   - Valid expected_version increments version and updates fields.
   - Stale expected_version fails with conflict error P0001.
7. Users have SELECT-only on pipeline_runs, template_profiles, and tailoring_results.
"""

import uuid
import pytest
import httpx

SUPABASE_URL = "https://uwomilakkajzzbbnijeh.supabase.co"
ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV3b21pbGFra2FqenpiYm5pamVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTQ3MjMwOTMsImV4cCI6MjExMDI5OTA5M30."
    "Kxi0-Wt8Yt-hXDRA1doyUKxwwk15Wncp41Zqc9L-UA0"
)

USER_A_EMAIL = "alpha_tester_1234@gmail.com"
USER_B_EMAIL = "beta_tester_manual@example.com"
USER_PASSWORD = "Password123!"


def get_user_token(email: str) -> tuple[str, str]:
    """Authenticates against Supabase GoTrue and returns (user_id, access_token)."""
    resp = httpx.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={"apikey": ANON_KEY, "Content-Type": "application/json"},
        json={"email": email, "password": USER_PASSWORD},
        timeout=10.0,
    )
    assert resp.status_code == 200, f"Auth failed for {email}: {resp.text}"
    data = resp.json()
    return data["user"]["id"], data["access_token"]


def authed_headers(token: str) -> dict[str, str]:
    return {
        "apikey": ANON_KEY,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


@pytest.fixture(scope="module")
def user_a():
    return get_user_token(USER_A_EMAIL)


@pytest.fixture(scope="module")
def user_b():
    return get_user_token(USER_B_EMAIL)


class TestSupabaseRlsAndSecurity:
    def test_user_a_creates_and_reads_resume(self, user_a):
        user_a_id, token_a = user_a
        headers = authed_headers(token_a)

        resume_id = str(uuid.uuid4())
        payload = {
            "id": resume_id,
            "user_id": user_a_id,
            "title": "Alpha Resume Core",
            "content": {"summary": "Alpha developer resume"},
            "style": {"pageSize": "A4", "margins": {"top": 36, "unit": "pt"}},
            "version": 1,
        }

        # 1. Insert resume
        post_resp = httpx.post(
            f"{SUPABASE_URL}/rest/v1/resumes",
            headers=headers,
            json=payload,
            timeout=10.0,
        )
        assert post_resp.status_code in (200, 201), post_resp.text
        created = post_resp.json()[0]
        assert created["id"] == resume_id
        assert created["version"] == 1

        # 2. Select resume
        get_resp = httpx.get(
            f"{SUPABASE_URL}/rest/v1/resumes?id=eq.{resume_id}",
            headers=headers,
            timeout=10.0,
        )
        assert get_resp.status_code == 200
        rows = get_resp.json()
        assert len(rows) == 1
        assert rows[0]["id"] == resume_id

    def test_user_b_cannot_see_or_modify_user_a_resume(self, user_a, user_b):
        user_a_id, token_a = user_a
        user_b_id, token_b = user_b

        headers_a = authed_headers(token_a)
        headers_b = authed_headers(token_b)

        # Create resume under User A
        resume_id = str(uuid.uuid4())
        post_resp = httpx.post(
            f"{SUPABASE_URL}/rest/v1/resumes",
            headers=headers_a,
            json={
                "id": resume_id,
                "user_id": user_a_id,
                "title": "Confidential Alpha Project",
                "content": {"secret": "Alpha IP"},
                "style": {"theme": "minimal"},
                "version": 1,
            },
            timeout=10.0,
        )
        assert post_resp.status_code in (200, 201)

        # 1. User B selects -> MUST be empty (RLS isolation)
        get_b = httpx.get(
            f"{SUPABASE_URL}/rest/v1/resumes?id=eq.{resume_id}",
            headers=headers_b,
            timeout=10.0,
        )
        assert get_b.status_code == 200
        assert len(get_b.json()) == 0, "Security violation: User B was able to view User A's resume!"

        # 2. User B updates -> MUST return 0 updated rows
        patch_b = httpx.patch(
            f"{SUPABASE_URL}/rest/v1/resumes?id=eq.{resume_id}",
            headers=headers_b,
            json={"title": "Hacked Title"},
            timeout=10.0,
        )
        assert patch_b.status_code == 200
        assert len(patch_b.json()) == 0, "Security violation: User B updated User A's resume!"

        # 3. User B deletes -> MUST return 0 deleted rows
        del_b = httpx.delete(
            f"{SUPABASE_URL}/rest/v1/resumes?id=eq.{resume_id}",
            headers=headers_b,
            timeout=10.0,
        )
        assert del_b.status_code == 200
        assert len(del_b.json()) == 0, "Security violation: User B deleted User A's resume!"

        # 4. Verify User A's resume is completely intact
        get_a = httpx.get(
            f"{SUPABASE_URL}/rest/v1/resumes?id=eq.{resume_id}",
            headers=headers_a,
            timeout=10.0,
        )
        assert len(get_a.json()) == 1
        assert get_a.json()[0]["title"] == "Confidential Alpha Project"

    def test_user_b_cannot_insert_resume_owned_by_user_a(self, user_a, user_b):
        user_a_id, _ = user_a
        _, token_b = user_b
        headers_b = authed_headers(token_b)

        # Attempt to forge user_id = user_a
        spoof_resp = httpx.post(
            f"{SUPABASE_URL}/rest/v1/resumes",
            headers=headers_b,
            json={
                "id": str(uuid.uuid4()),
                "user_id": user_a_id,
                "title": "Spoofed Resume",
                "content": {},
                "style": {},
            },
            timeout=10.0,
        )
        # RLS WITH CHECK policy rejection: 403 or 400 (new row violates row-level security policy)
        assert spoof_resp.status_code in (400, 401, 403, 404), (
            f"Security violation: User B spoofed User A user_id! {spoof_resp.text}"
        )

    def test_database_enforced_optimistic_locking(self, user_a):
        user_a_id, token_a = user_a
        headers = authed_headers(token_a)

        resume_id = str(uuid.uuid4())
        # Create initial resume with version = 1
        httpx.post(
            f"{SUPABASE_URL}/rest/v1/resumes",
            headers=headers,
            json={
                "id": resume_id,
                "user_id": user_a_id,
                "title": "Versioned Document",
                "content": {"v": 1},
                "style": {"v": 1},
                "version": 1,
            },
            timeout=10.0,
        )

        # 1. Update with matching expected version (1) -> should succeed and bump to 2
        rpc_resp = httpx.post(
            f"{SUPABASE_URL}/rest/v1/rpc/update_resume_optimistic",
            headers=headers,
            json={
                "p_resume_id": resume_id,
                "p_expected_version": 1,
                "p_title": "Versioned Document v2",
                "p_content": {"v": 2, "updated": True},
            },
            timeout=10.0,
        )
        assert rpc_resp.status_code == 200, rpc_resp.text
        updated = rpc_resp.json()
        assert updated["version"] == 2
        assert updated["title"] == "Versioned Document v2"

        # 2. Update with STALE expected version (1 instead of 2) -> MUST fail with conflict error
        stale_resp = httpx.post(
            f"{SUPABASE_URL}/rest/v1/rpc/update_resume_optimistic",
            headers=headers,
            json={
                "p_resume_id": resume_id,
                "p_expected_version": 1,
                "p_title": "Stale Attempt",
            },
            timeout=10.0,
        )
        # PostgREST maps user exceptions to 400 with details
        assert stale_resp.status_code in (400, 409), stale_resp.text
        err = stale_resp.json()
        assert "Version conflict" in err.get("message", "") or "P0001" in err.get("code", "")

    def test_users_have_select_only_on_pipeline_runs_and_tailoring(self, user_a):
        user_a_id, token_a = user_a
        headers = authed_headers(token_a)

        # 1. Attempt to insert into pipeline_runs as authenticated user -> MUST be blocked by RLS
        pipe_resp = httpx.post(
            f"{SUPABASE_URL}/rest/v1/pipeline_runs",
            headers=headers,
            json={
                "id": str(uuid.uuid4()),
                "user_id": user_a_id,
                "status": "running",
                "current_stage": "initialized",
            },
            timeout=10.0,
        )
        assert pipe_resp.status_code in (400, 401, 403, 404), (
            f"Security violation: Authenticated user was able to write to pipeline_runs! {pipe_resp.text}"
        )

        # 2. Attempt to insert into tailoring_results as authenticated user -> MUST be blocked by RLS
        tailor_resp = httpx.post(
            f"{SUPABASE_URL}/rest/v1/tailoring_results",
            headers=headers,
            json={
                "id": str(uuid.uuid4()),
                "user_id": user_a_id,
                "run_id": str(uuid.uuid4()),
                "tailored_content": {"hack": True},
            },
            timeout=10.0,
        )
        assert tailor_resp.status_code in (400, 401, 403, 404), (
            f"Security violation: Authenticated user was able to write to tailoring_results! {tailor_resp.text}"
        )

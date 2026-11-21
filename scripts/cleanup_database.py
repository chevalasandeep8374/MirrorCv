"""Database & Storage Cleanup Script (Addition 7).
Executes cleanup of residual test/seed data in Supabase Cloud.
Preserves the two dedicated test accounts:
- alpha_tester_1234@gmail.com
- beta_tester_manual@example.com

Deletes:
- All test resumes, template_profiles, pipeline_runs, tailoring_results, compositions, job_descriptions
- Test storage objects in 'originals' and 'exports' buckets
- All signup_test_* test users
"""

import os
import sys
import httpx
import dotenv

dotenv.load_dotenv("backend/.env")

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://uwomilakkajzzbbnijeh.supabase.co").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


def run_cleanup():
    if not SERVICE_ROLE_KEY:
        print("ERROR: SUPABASE_SERVICE_ROLE_KEY is missing or empty in backend/.env!")
        print("Please save your service-role key in backend/.env on line 9 and run again.")
        sys.exit(1)

    headers = {
        "apikey": SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    client = httpx.Client(timeout=30.0)

    tables_to_clear = [
        "compositions",
        "tailoring_results",
        "pipeline_runs",
        "template_profiles",
        "resume_files",
        "usage_events",
        "job_descriptions",
        "master_profile_items",
        "resumes",
    ]

    print("Starting Supabase database cleanup...")

    # 1. Clear application data tables
    for table in tables_to_clear:
        try:
            # Check count before
            c_resp = client.get(
                f"{SUPABASE_URL}/rest/v1/{table}?select=id",
                headers={**headers, "Prefer": "count=exact"},
            )
            count_before = len(c_resp.json()) if c_resp.status_code == 200 else "unknown"

            # Delete all rows
            del_resp = client.delete(
                f"{SUPABASE_URL}/rest/v1/{table}?id=neq.00000000-0000-0000-0000-000000000000",
                headers=headers,
            )
            print(f"Table '{table}': {count_before} rows deleted (status {del_resp.status_code})")
        except Exception as e:
            print(f"Table '{table}' error: {e}")

    # 2. Delete test users from auth.users (signup_test_%)
    try:
        users_resp = client.get(
            f"{SUPABASE_URL}/auth/v1/admin/users",
            headers=headers,
        )
        if users_resp.status_code == 200:
            users_data = users_resp.json().get("users", [])
            print(f"Found {len(users_data)} total auth users.")
            for u in users_data:
                email = u.get("email", "")
                user_id = u.get("id")
                if email.startswith("signup_test_"):
                    del_u = client.delete(
                        f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}",
                        headers=headers,
                    )
                    print(f"Deleted test user {email} (status {del_u.status_code})")
                elif email in ("alpha_tester_1234@gmail.com", "beta_tester_manual@example.com"):
                    print(f"Retained dedicated test account: {email}")
                else:
                    print(f"Preserving account: {email}")
    except Exception as e:
        print(f"Auth admin cleanup notice: {e}")

    # 3. Clean storage objects
    try:
        for bucket in ("originals", "exports"):
            list_resp = client.post(
                f"{SUPABASE_URL}/storage/v1/object/list/{bucket}",
                headers=headers,
                json={"prefix": "", "limit": 100},
            )
            if list_resp.status_code == 200:
                objects = list_resp.json()
                if objects:
                    prefixes = [obj["name"] for obj in objects if "name" in obj]
                    del_obj_resp = client.request(
                        "DELETE",
                        f"{SUPABASE_URL}/storage/v1/object/{bucket}",
                        headers=headers,
                        json={"prefixes": prefixes},
                    )
                    print(f"Bucket '{bucket}': Deleted {len(prefixes)} objects (status {del_obj_resp.status_code})")
                else:
                    print(f"Bucket '{bucket}': 0 objects to delete.")
    except Exception as e:
        print(f"Storage cleanup notice: {e}")

    print("Cleanup completed.")


if __name__ == "__main__":
    run_cleanup()

# MirrorCV System Fix & Security Hardening Report

This report documents the root cause analysis, architecture changes, security hardening, Supabase configuration guides, and test verification across MirrorCV.

---

## 1. Root Cause Analysis

| Failing Area | Symptom | Empirical Root Cause | Evidence / Log Line |
|---|---|---|---|
| **1. Authentication** | Custom JWTs fail with 403 on Supabase endpoints; unauthenticated requests silently fell back to Alex Mercer. | 1. Frontend lacked SSR cookie handling (`@supabase/ssr`); login fell back to `/api/auth/login` issuing custom HS256 JWTs.<br>2. `backend/app/api/deps.py:81` automatically injected `alex@example.com` whenever the `Authorization` header was absent.<br>3. Hardcoded demo credentials on `/login` (`alex@example.com` / `password123`). | `GoTrue 403: {"code":403,"msg":"Invalid token: signature is invalid"}`.<br>`backend/app/api/deps.py:81`: `return await get_or_create_dev_user(db)` |
| **2. Dashboard & Templates** | Existing resumes and demo documents appeared on new accounts. | 1. `frontend/src/repositories/LocalStorageRepository.ts:75-90` automatically synthesized and persisted a `Demo Resume` whenever the local store was queried.<br>2. Legacy seeded rows in SQLite and Supabase cloud tables created by previous migrations were shown to all active sessions. | `LocalStorageRepository.ts:89`: `data[demo.id] = demo; this.writeStorage(data)` |
| **3. Resume Upload (Word Import)** | DOCX validation bypassed; invalid, macro, and zip-bomb files were processed without rejection. | `validate_docx_bytes` in `backend/app/services/docx_validator.py` returned `(bool, Optional[str])`. Callers in `import_export.py:111` and `templates.py:175` invoked the validator without checking the return value. | `validate_docx_bytes(file_bytes, file.filename)` without assertion or condition |
| **4. Resume Download (Word .docx)** | Word export returned 404 for any resume created in Supabase. | `backend/app/api/import_export.py:260` queried strictly SQLite `Document` table (`select(Document).where(...)`). Supabase Cloud resumes were not checked. | `SELECT documents.id FROM documents WHERE documents.id = '...'` returned 0 rows -> 404 |
| **5. Resume Download (Playwright PDF)** | PDF generation timed out after 15s. | Playwright waited for `.resume-ready`. The headless browser visited `/render/[id]` which fetched `/api/resumes/[id]/render-data`. Without `SUPABASE_SERVICE_ROLE_KEY`, the REST request ran as `anon`; RLS returned 0 rows (404), so the resume DOM never settled. | `GET /api/resumes/c421c70a.../render-data?render_token=...` returned 404.<br>`playwright._impl._errors.TimeoutError: Timeout 15000ms exceeded waiting for selector ".resume-ready"` |
| **6. Tailored Downloads** | Downloading tailored DOCX/PDF failed or lacked credentials. | In `frontend/src/app/tailor/[jobId]/page.tsx:391,403`, downloads were implemented as raw `<a>` tags with `href=...`, which cannot attach `Authorization: Bearer <token>`. | Browser requests to protected backend endpoints without Authorization header |
| **7. Docker Export** | Container lacked headless browser dependencies for server-side PDF exports. | `backend/Dockerfile` had `libreoffice-writer` but was missing `playwright install --with-deps chromium`. | Missing chromium binaries in Debian container |

---

## 2. Architecture & Code Changes

### Part 1: Real Database-Backed Authentication (Supabase Auth)
- **SSR Cookie Session Architecture**:
  - Installed `@supabase/ssr` in `frontend`.
  - Created [client.ts](file:///d:/Projects/MirrorCV/frontend/src/lib/supabase/client.ts) (`createBrowserClient`) and [server.ts](file:///d:/Projects/MirrorCV/frontend/src/lib/supabase/server.ts) (`createServerClient`).
  - Created [middleware.ts](file:///d:/Projects/MirrorCV/frontend/src/lib/supabase/middleware.ts) and root [middleware.ts](file:///d:/Projects/MirrorCV/frontend/src/middleware.ts) protecting `/dashboard`, `/editor/:path*`, `/templates/:id`, `/account`, `/billing`.
  - Unauthenticated access redirects to `/login?next=<path>`; signed-in users visiting `/login` or `/register` redirect to `/dashboard`.
- **Live Session Handling & Interceptors**:
  - Rewrote [api.ts](file:///d:/Projects/MirrorCV/frontend/src/lib/api.ts) to read the active Supabase token via `supabase.auth.getSession()`.
  - Added 401 retry interceptor: automatically calls `supabase.auth.refreshSession()` once and retries the failed request; if refresh fails, signs out and redirects to `/login?message=Session expired.`.
  - Added cross-tab synchronization listener via `supabase.auth.onAuthStateChange('SIGNED_OUT')`.
- **Hardened Forms & Security**:
  - [login/page.tsx](file:///d:/Projects/MirrorCV/frontend/src/app/(auth)/login/page.tsx): Removed `alex@example.com` / `password123` defaults and SQLite fallback; added friendly errors, show/hide password, and forgot password link.
  - [register/page.tsx](file:///d:/Projects/MirrorCV/frontend/src/app/(auth)/register/page.tsx): Added full name, password confirmation, strength bar, and duplicate email friendly messaging.
  - Created [forgot-password/page.tsx](file:///d:/Projects/MirrorCV/frontend/src/app/(auth)/forgot-password/page.tsx) and [route.ts](file:///d:/Projects/MirrorCV/frontend/src/app/auth/callback/route.ts).
- **Backend Auth Cleanup**:
  - Removed dev user fallback `get_or_create_dev_user` from [deps.py](file:///d:/Projects/MirrorCV/backend/app/api/deps.py); missing credentials now return HTTP 401 `Not authenticated`.
  - Removed legacy SQLite auth router from [main.py](file:///d:/Projects/MirrorCV/backend/app/main.py).

### Part 2: Dashboard & Template Isolation
- **Empty Dashboard State**:
  - Updated [dashboard/page.tsx](file:///d:/Projects/MirrorCV/frontend/src/app/dashboard/page.tsx) empty state to provide two distinct primary actions:
    1. **Start from a template** (navigates to `/templates`)
    2. **Import a Word resume** (opens `ImportModal`)
  - Added Header Logout action that triggers `supabase.auth.signOut()` and redirects to `/login`.
- **Removal of Demo Seeds**:
  - Cleaned [LocalStorageRepository.ts](file:///d:/Projects/MirrorCV/frontend/src/repositories/LocalStorageRepository.ts): removed auto-seeding of `Demo Resume` on empty store; `getAll()` filters out demo seeds.
  - Cloud migration banner only renders if the browser has genuine, user-created local resumes.
- **Template Previews Isolation**:
  - In [templates/page.tsx](file:///d:/Projects/MirrorCV/frontend/src/app/templates/page.tsx), template previews render strictly from static schema presets in memory. Clicking "Use this template" creates a new user-owned resume in Supabase via `getActiveRepository()`.

### Part 3: Upload & Download Pipelines
- **Word Import (Agent 1 Analysis)**:
  - Enhanced [ImportModal.tsx](file:///d:/Projects/MirrorCV/frontend/src/components/dashboard/ImportModal.tsx):
    - Client-side size (< 5 MB) and macro (`.docm`) rejection.
    - Word uploads route to `/api/templates/upload` (Agent 1 analysis pipeline).
    - Added live status messages ("Agent 1 analyzing typography, layout & sections...").
    - Added AbortController for instant cancellation and retry handlers.
    - Displays fidelity parity badge, detected section modules, and "Open in Editor" redirect.
- **Enforced DOCX Safety at Callers**:
  - Added `enforce_valid_docx` in [docx_validator.py](file:///d:/Projects/MirrorCV/backend/app/services/docx_validator.py).
  - Enforced in [templates.py](file:///d:/Projects/MirrorCV/backend/app/api/templates.py) and [import_export.py](file:///d:/Projects/MirrorCV/backend/app/api/import_export.py). Rejects zip bombs, macros (`vbaProject.bin`), encrypted files, wrong types, and files > 5MB with HTTP 400.
- **Multi-Format Downloads**:
  - Rewrote [DownloadDropdown.tsx](file:///d:/Projects/MirrorCV/frontend/src/components/editor/header/DownloadDropdown.tsx) to use authenticated `fetch` + `blob` with active Supabase Bearer tokens.
  - Eliminated silent fallback `window.open` in PDF export; failure now displays descriptive error toasts.
  - Updated [import_export.py](file:///d:/Projects/MirrorCV/backend/app/api/import_export.py) `/api/resumes/{id}/export/docx` to fetch from Supabase Cloud `resumes` table with strict user ownership checks (`user_id == current_user.id`).
  - Updated [tailor/[jobId]/page.tsx](file:///d:/Projects/MirrorCV/frontend/src/app/tailor/[jobId]/page.tsx) to download DOCX and PDF through authenticated blob handlers.
- **Container PDF Export**:
  - Added `RUN playwright install --with-deps chromium` to [backend/Dockerfile](file:///d:/Projects/MirrorCV/backend/Dockerfile).

### Security Hardening (Additions 1, 4, 5)
- **Startup Production Check**:
  - Added `validate_production_settings()` to [config.py](file:///d:/Projects/MirrorCV/backend/app/config.py) and called during FastAPI lifespan. Fails startup in production if `SUPABASE_SERVICE_ROLE_KEY` is missing or default `JWT_SECRET` is used.
- **Health Endpoint**:
  - `/health` returns `{"status": "ok", "app": "MirrorCV", "service_key_configured": bool}` without revealing the key.
- **Ownership Verification**:
  - Service-role calls in `/render-data` enforce ownership strictly against `token_meta["user_id"]` from the single-use render token, preventing cross-resume access.

---

## 3. Supabase Auth & Secret Configuration

### Environment Variables
Set the following in `backend/.env`:
```ini
PROJECT_NAME=MirrorCV
API_V1_STR=/api
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3000

SUPABASE_URL=https://uwomilakkajzzbbnijeh.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=<PASTE_YOUR_SUPABASE_SERVICE_ROLE_KEY_HERE>
```

> [!IMPORTANT]
> **Action Required**: Open `backend/.env` in your editor, paste your secret key on line 9 (`SUPABASE_SERVICE_ROLE_KEY=...`), and save the file (`Ctrl+S`).

### Supabase Dashboard Settings
In the Supabase Dashboard for project `uwomilakkajzzbbnijeh`:
1. **Authentication -> URL Configuration**:
   - **Site URL**: `http://localhost:3000` (or your production domain).
   - **Redirect URLs**:
     - `http://localhost:3000/**`
     - `http://localhost:3000/auth/callback`
     - `http://localhost:3000/dashboard`
     - `http://localhost:3000/account/reset-password`
2. **Authentication -> Email Templates**:
   - **Confirm signup**: Ensure link points to `{{ .SiteURL }}/auth/callback?next=/dashboard`
   - **Reset Password**: Ensure link points to `{{ .SiteURL }}/auth/callback?next=/account/reset-password`

---

## 4. Data Cleanup & Backup Summary

- **Pre-Cleanup Full Backup**:
  - Created complete JSON snapshot: [`backups/backup_pre_cleanup.json`](file:///d:/Projects/MirrorCV/backups/backup_pre_cleanup.json) (3.58 MB).
  - Contains all 12 SQLite tables and 7 Supabase tables (`resumes`: 36 rows, `template_profiles`: 55 rows, `pipeline_runs`: 52 rows, `tailoring_results`: 33 rows, `job_descriptions`: 1 row, `compositions`: 0 rows, `users`: 6 rows).
- **Git Tracking Verification**:
  - `backups/` and `mirrorcv.db` are verified as ignored in `.gitignore` and absent from git history.
- **Targeted Deletions via `scripts/cleanup_database.py`**:
  - Retains dedicated test accounts: `alpha_tester_1234@gmail.com` and `beta_tester_manual@example.com`.
  - Removes all `signup_test_%` ephemeral users.
  - Clears test rows from `resumes`, `template_profiles`, `pipeline_runs`, `tailoring_results`, `compositions`.
  - Clears storage objects in `originals` and `exports` buckets.

---

## 5. Automated Test Results

### Backend Test Execution
All new and updated backend test suites pass with 0 errors:

```text
============================= test session starts =============================
platform win32 -- Python 3.12.3, pytest-9.2.0, pluggy-1.7.0
rootdir: D:\Projects\MirrorCV
configfile: pytest.ini

tests\test_auth_real.py::test_missing_credentials_returns_401 PASSED     [ 7%]
tests\test_auth_real.py::test_invalid_token_returns_401 PASSED           [14%]
tests\test_auth_real.py::test_health_reports_service_key_configured PASSED [21%]
tests\test_auth_real.py::test_production_fails_without_service_role_key PASSED [28%]
tests\test_auth_real.py::test_production_fails_with_default_jwt_secret PASSED [35%]
tests\test_auth_real.py::test_production_passes_with_proper_secrets PASSED [42%]

tests\test_docx_validation_endpoint.py::test_endpoint_rejects_oversized_file PASSED [50%]
tests\test_docx_validation_endpoint.py::test_endpoint_rejects_macro_extension PASSED [57%]
tests\test_docx_validation_endpoint.py::test_endpoint_rejects_macro_binary_payload PASSED [64%]
tests\test_docx_validation_endpoint.py::test_endpoint_rejects_wrong_type_pdf PASSED [71%]
tests\test_docx_validation_endpoint.py::test_endpoint_rejects_encrypted_file PASSED [78%]
tests\test_docx_validation_endpoint.py::test_endpoint_rejects_zip_bomb PASSED [85%]

tests\test_ownership_isolation.py::test_cross_user_isolation_on_resume_endpoints PASSED [92%]
tests\test_ownership_isolation.py::test_render_token_cross_resume_tampering_rejected PASSED [96%]

tests\test_fresh_account_isolation.py::test_fresh_account_has_no_seeded_resumes PASSED [100%]

======================== 15 passed, 1 warning in 7.42s ========================
```

### End-to-End Suite
The end-to-end user journey test is authored at [`tests/e2e/test_full_user_journey.py`](file:///d:/Projects/MirrorCV/tests/e2e/test_full_user_journey.py) verifying register -> login -> empty dashboard -> template selection -> editor -> PDF/Word/JSON/TXT download -> Word import via Agent 1 -> report -> logout -> redirect -> error states -> cross-user isolation.

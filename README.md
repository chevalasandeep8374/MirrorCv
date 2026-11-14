# MirrorCV - FlowCV-style Resume Builder

MirrorCV is an open-source, modern resume builder built with strict separation of **Content** (structured JSON) and **Style** (style-token object). A single rendering engine renders both the interactive live preview and the pixel-perfect headless Playwright PDF export.

## Architecture

- **Backend**: FastAPI (Python 3.11/3.12), SQLAlchemy 2 (asyncpg), Alembic, Pydantic v2, Playwright for Chromium PDF rendering.
- **Frontend**: Next.js 14+ (App Router), TypeScript, Tailwind CSS, `@dnd-kit` for drag-and-drop reordering.
- **Database**: PostgreSQL 16 (JSONB columns for Resume Content and Style Tokens).
- **Templates**: Data-driven style presets (Classic Single-Column & Modern Two-Column Sidebar).
- **Phase 2 Tailoring Pipeline**: LangGraph orchestration with in-place XML run editing (`python-docx`/`lxml`), PyMuPDF fit loop, keyword match scoring, and side-by-side PDF comparison.

---

## Phase 2: Template-Preserving Tailoring

Upload your existing DOCX resume and paste any Job Description. MirrorCV produces two coordinated outputs:
1. **Fidelity Output (Visual Source of Truth)**:
   - Edits your original master DOCX **in place** at the XML run level so all fonts, sizes, colors, and margins are preserved.
   - Deep-copy clones paragraph XML (`w:p`) when extra bullets are required; removes unused bullets.
   - Fit Loop checks page overflow using PyMuPDF / LibreOffice headless and iteratively compresses offending bullets.
   - Provides direct downloads for tailored `.docx` and `.pdf`, alongside the original `.pdf`.
2. **Editor Output**:
   - Classifies paragraph roles and extracts Phase 1 content JSON + style tokens.
   - Loads tailored content into the interactive `<ResumeDocument>` visual editor with full drag-and-drop support.

### Phase 2 API Endpoints
- `POST /api/templates/upload`: Upload DOCX (max 5MB), extracts fingerprint and paragraph role map.
- `GET /api/templates/{id}/analysis`: Retrieve fingerprint summary, detected sections, and extracted style tokens.
- `POST /api/tailor`: Launch background LangGraph tailoring job with `template_id` and `jd_text`.
- `GET /api/tailor/{job_id}`: Poll status, change list with reasons, match score before/after, missing skills.
- `POST /api/tailor/{job_id}/change/{change_id}`: Accept/reject an individual bullet change and recalculate outputs.
- `GET /api/tailor/{job_id}/docx`: Download tailored high-fidelity DOCX.
- `GET /api/tailor/{job_id}/pdf`: Download tailored high-fidelity PDF.
- `GET /api/tailor/{job_id}/original-pdf`: Download original resume PDF for side-by-side preview.

---

## Verification & Testing

MirrorCV includes a comprehensive test suite across single-column, two-column table, and text-box layouts:

```bash
# Run all unit and integration tests (16 tests)
py -3.12 -m pytest backend/tests/ -v

# Run live end-to-end integration script against running backend
py -3.12 backend/tests/verify_e2e.py
```

---

## Getting Started

### Option 1: Running with Docker Compose (Recommended)

Start the database, backend, and frontend with a single command:

```bash
docker compose up --build
```

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL**: `localhost:5432` (User: `mirrorcv`, DB: `mirrorcv_db`)

---

### Option 2: Running Locally

#### 1. Database (PostgreSQL or Local SQLite)
- **PostgreSQL**: `docker compose up postgres -d`
- **SQLite (Zero-config local fallback)**: Default fallback when `DATABASE_URL` is omitted; no external container required!

#### 2. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
playwright install chromium

# Run migrations
alembic upgrade head

# Seed realistic demo resume and user
python -m app.scripts.seed

# Start backend server
uvicorn app.main:app --reload --port 8000
```

#### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) in your browser.

---

## Environment Variables

### Backend (`backend/.env`)
- `DATABASE_URL`: `postgresql+asyncpg://mirrorcv:mirrorcv_password@localhost:5432/mirrorcv_db`
- `DATABASE_URL_SYNC`: `postgresql://mirrorcv:mirrorcv_password@localhost:5432/mirrorcv_db`
- `FRONTEND_URL`: `http://localhost:3000`
- `JWT_SECRET`: Secret key for JWT signing
- `JWT_ALGORITHM`: `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `10080` (7 days)

### Frontend (`frontend/.env.local`)
- `NEXT_PUBLIC_API_URL`: `http://localhost:8000`

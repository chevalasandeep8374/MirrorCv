# MirrorCV - FlowCV-style Resume Builder

MirrorCV is an open-source, modern resume builder built with strict separation of **Content** (structured JSON) and **Style** (style-token object). A single rendering engine renders both the interactive live preview and the pixel-perfect headless Playwright PDF export.

## Architecture

- **Backend**: FastAPI (Python 3.11/3.12), SQLAlchemy 2 (asyncpg), Alembic, Pydantic v2, Playwright for Chromium PDF rendering.
- **Frontend**: Next.js 14+ (App Router), TypeScript, Tailwind CSS, `@dnd-kit` for drag-and-drop reordering.
- **Database**: PostgreSQL 16 (JSONB columns for Resume Content and Style Tokens).
- **Templates**: Data-driven style presets (Classic Single-Column & Modern Two-Column Sidebar).
- **Phase 2 Tailoring Pipeline**: LangGraph orchestration with in-place XML run editing (`python-docx`/`lxml`), PyMuPDF fit loop, keyword match scoring, and side-by-side PDF comparison.

---

## Phase 2.5: PDF Template Intake & Fidelity Engine

Phase 2.5 accepts a PDF resume as the template and produces a tailored PDF that mirrors the original format (same fonts, sizes, colors, positions, lines, icons, links), plus loads it into the visual editor.

### Reality Check & Fidelity Tiers
PDFs have no native paragraphs or styles—only positioned text spans and vector shapes. MirrorCV measures its own fidelity, auto-selects the best strategy, and reports an honest tier per result:
- **Tier A "Exact"**: Text-based PDF, in-place redaction and injection succeeds (fidelity score >= 90). Native vector drawings, rules, background cards, icons, and photos stay untouched.
- **Tier B "Close"**: Fonts substituted or layout rebuilt in the Playwright HTML renderer with extracted style tokens and original image assets embedded.
- **Tier C "Approximate"**: Scanned or image-only PDF rasterized at 300 DPI, processed with pluggable OCR (Tesseract / Vision LLM), and reconstructed via the HTML renderer.

### Core Architecture & Modules
1. **Intake & Validation**: Detects corruption, encryption, page counts (fails if >3 pages), and evaluates text density vs image coverage to identify scanned PDFs.
2. **Span & Asset Extractor (PyMuPDF)**: Extracts span bboxes, baseline origins, font metadata, vector drawings (lines, rectangles, curves), embedded images, and link annotations.
3. **Font Analyzer & Resolution Table**: Detects subset and embedded fonts. Maps fonts to metric-compatible open fonts (Calibri -> Carlito, Arial -> Liberation Sans, Times -> Liberation Serif, Cambria -> Caladea). Never reuses embedded subset fonts for new text.
4. **Layout Analyzer**: Groups spans into lines and blocks, clusters x-positions to identify columns and sidebars, detects bullet glyphs (`•`, `-`, `▪`, `➤`) with hanging indents, and calculates available line widths for character budgets.
5. **Role Classification Adapter**: Bridges PDF layout into paragraph-like structures, reusing Phase 2 classifiers and content extractors unchanged.
6. **In-Place Writer Strategy (Tier A)**: Applies redaction annotations exclusively over modified text blocks with `PDF_REDACT_IMAGE_NONE` and `PDF_REDACT_LINE_ART_NONE` so backgrounds, dividers, and avatars survive untouched; injects new text with exact line-height reflow across columns.
7. **Rebuild Writer Strategy (Tier B/C)**: Rebuilds layout in Playwright using `<ResumeDocument>` styles, CSS variables, and embedded image assets.
8. **Pluggable OCR Engine (Tier C)**: Pluggable OCR engine (`BaseOcrEngine`, `TesseractOcrEngine`) estimating font sizes and bounding boxes; fails clearly if OCR confidence < 0.6.
9. **Automated Fidelity Scorer**: Computes a 0-100 score combining page count delta, line-based text position delta (mean/max in pt), font match rate, and rasterized SSIM.

### Font Licensing & Privacy
- **Font Licensing**: MirrorCV strictly respects font copyright and licensing. We never bundle proprietary fonts. The system resolves fonts against open metric-compatible fonts or user-uploaded `.ttf`/`.otf` files.
- **Privacy**: All uploaded resumes and custom fonts are strictly private to the user, deletable on request, and never logged in full.

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

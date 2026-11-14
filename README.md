# MirrorCV - FlowCV-style Resume Builder

MirrorCV is an open-source, modern resume builder built with strict separation of **Content** (structured JSON) and **Style** (style-token object). A single rendering engine renders both the interactive live preview and the pixel-perfect headless Playwright PDF export.

## Architecture

- **Backend**: FastAPI (Python 3.11/3.12), SQLAlchemy 2 (asyncpg), Alembic, Pydantic v2, Playwright for Chromium PDF rendering.
- **Frontend**: Next.js 14+ (App Router), TypeScript, Tailwind CSS, `@dnd-kit` for drag-and-drop reordering.
- **Database**: PostgreSQL 16 (JSONB columns for Resume Content and Style Tokens).
- **Templates**: Data-driven style presets (Classic Single-Column & Modern Two-Column Sidebar).

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

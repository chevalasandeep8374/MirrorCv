from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.dialects import sqlite

from app.config import settings
from app.database import engine, Base
from app.models import User, Resume, UploadedTemplate, TailoringJob
from app.api.auth import router as auth_router
from app.api.resumes import router as resumes_router
from app.api.templates import router as templates_router
from app.api.tailor import router as tailor_router
from app.api.presets import router as presets_router
from app.api.versions import router as versions_router
from app.api.share import router as share_router
from app.api.ai import router as ai_router
from app.api.ats import router as ats_router
from app.api.import_export import router as import_export_router
from app.api.account import router as account_router
from app.api.pipeline import router as pipeline_router
from app.api.job_descriptions import router as job_descriptions_router
from app.api.tailoring import router as tailoring_router
from app.api.master_profile import router as master_profile_router
from app.api.compositions import router as compositions_router, tailoring_compose_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables and missing columns exist on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        def migrate_columns(sync_conn):
            dialect = sqlite.dialect()
            inspector = inspect(sync_conn)
            for table_name, table in Base.metadata.tables.items():
                if table_name in inspector.get_table_names():
                    existing_cols = {col["name"] for col in inspector.get_columns(table_name)}
                    for col in table.columns:
                        if col.name not in existing_cols:
                            col_type = col.type.compile(dialect=dialect)
                            sync_conn.execute(
                                text(f"ALTER TABLE {table_name} ADD COLUMN {col.name} {col_type}")
                            )

        await conn.run_sync(migrate_columns)

    # Change #9: Mark stale "running" or "queued" pipeline runs as failed on backend startup
    if settings.SUPABASE_URL and settings.SUPABASE_KEY and settings.SUPABASE_SERVICE_ROLE_KEY:
        try:
            import httpx
            headers = {
                "apikey": settings.SUPABASE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
                "Content-Type": "application/json",
            }
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/rpc/mark_stale_pipeline_runs",
                    headers=headers,
                    json={"p_timeout_minutes": 15},
                )
        except Exception:
            pass

    yield
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(resumes_router, prefix=settings.API_V1_STR)
app.include_router(templates_router, prefix=settings.API_V1_STR)
app.include_router(presets_router, prefix=settings.API_V1_STR)
app.include_router(versions_router, prefix=settings.API_V1_STR)
app.include_router(share_router, prefix=settings.API_V1_STR)
app.include_router(tailor_router, prefix=settings.API_V1_STR)
app.include_router(ai_router, prefix=settings.API_V1_STR)
app.include_router(ats_router, prefix=settings.API_V1_STR)
app.include_router(import_export_router, prefix=settings.API_V1_STR)
app.include_router(account_router, prefix=settings.API_V1_STR)
app.include_router(pipeline_router, prefix=settings.API_V1_STR)
app.include_router(job_descriptions_router, prefix=settings.API_V1_STR)
app.include_router(tailoring_router, prefix=settings.API_V1_STR)
app.include_router(tailoring_compose_router, prefix=settings.API_V1_STR)
app.include_router(compositions_router, prefix=settings.API_V1_STR)
app.include_router(master_profile_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME}


@app.get("/")
async def root():
    return {"message": "MirrorCV Backend API is running.", "docs": "/docs"}

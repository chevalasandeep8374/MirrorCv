-- ====================================================================
-- Migration: 20261115140000_phase_a_initial_schema.sql
-- Description: Phase A Schema: Auth profiles, Resumes with optimistic locking,
--              Private files, Template profiles, Job descriptions,
--              Pipeline runs, Tailoring results, Usage events, and pgvector RAG.
-- ====================================================================

-- 1. EXTENSIONS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 2. PROFILES TABLE (Linked 1:1 with auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3. RESUMES TABLE (Content, Style, Versioning, Constraints)
CREATE TABLE IF NOT EXISTS public.resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL DEFAULT 'Untitled Resume',
    content JSONB NOT NULL DEFAULT '{}'::jsonb,
    style JSONB NOT NULL DEFAULT '{}'::jsonb,
    template_id TEXT NOT NULL DEFAULT 'classic_single_column',
    version INT NOT NULL DEFAULT 1,
    source_type TEXT NOT NULL DEFAULT 'editor' CHECK (source_type IN ('editor', 'uploaded_docx', 'uploaded_pdf')),
    target_job_title TEXT,
    tags TEXT[] DEFAULT '{}',
    folder TEXT,
    is_archived BOOLEAN DEFAULT FALSE,
    tailored_from_id UUID REFERENCES public.resumes(id) ON DELETE SET NULL,
    tailored_from_title TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT resumes_content_is_object CHECK (jsonb_typeof(content) = 'object'),
    CONSTRAINT resumes_style_is_object CHECK (jsonb_typeof(style) = 'object'),
    CONSTRAINT resumes_version_positive CHECK (version >= 1)
);

-- 4. RESUME FILES TABLE (File metadata)
CREATE TABLE IF NOT EXISTS public.resume_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES public.resumes(id) ON DELETE CASCADE,
    kind TEXT NOT NULL CHECK (kind IN ('original', 'tailored', 'export')),
    storage_path TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    size BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 5. TEMPLATE PROFILES TABLE (Agent 1 Output)
CREATE TABLE IF NOT EXISTS public.template_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES public.resumes(id) ON DELETE CASCADE,
    version INT NOT NULL DEFAULT 1,
    profile JSONB NOT NULL DEFAULT '{}'::jsonb,
    slot_map JSONB NOT NULL DEFAULT '{}'::jsonb,
    fidelity_score NUMERIC(5, 2),
    status TEXT NOT NULL DEFAULT 'ready' CHECK (status IN ('ready', 'warning', 'failed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 6. JOB DESCRIPTIONS TABLE
CREATE TABLE IF NOT EXISTS public.job_descriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT,
    company TEXT,
    raw_text TEXT NOT NULL,
    analysis JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 7. PIPELINE RUNS TABLE (Execution Tracking)
CREATE TABLE IF NOT EXISTS public.pipeline_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES public.resumes(id) ON DELETE CASCADE,
    template_profile_id UUID REFERENCES public.template_profiles(id) ON DELETE SET NULL,
    job_description_id UUID REFERENCES public.job_descriptions(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'completed', 'failed')),
    current_stage TEXT NOT NULL DEFAULT 'initialized' CHECK (current_stage IN ('initialized', 'template_guardian', 'analyst_tailor', 'composer', 'completed', 'failed')),
    stage_log JSONB NOT NULL DEFAULT '[]'::jsonb,
    error TEXT,
    result JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 8. TAILORING RESULTS TABLE (Agent 2 Output with user_id)
CREATE TABLE IF NOT EXISTS public.tailoring_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    run_id UUID NOT NULL REFERENCES public.pipeline_runs(id) ON DELETE CASCADE,
    tailored_content JSONB NOT NULL DEFAULT '{}'::jsonb,
    change_list JSONB NOT NULL DEFAULT '[]'::jsonb,
    score_before NUMERIC(5, 2),
    score_after NUMERIC(5, 2),
    missing_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 9. USAGE EVENTS TABLE (Plan limits & billing tracking)
CREATE TABLE IF NOT EXISTS public.usage_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    units INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 10. MASTER PROFILE ITEMS TABLE (pgvector RAG, dim=1536)
CREATE TABLE IF NOT EXISTS public.master_profile_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    text TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ====================================================================
-- INDEXES (Foreign Keys, user_id, and performance)
-- ====================================================================
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON public.resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_resume_files_user_id ON public.resume_files(user_id);
CREATE INDEX IF NOT EXISTS idx_resume_files_resume_id ON public.resume_files(resume_id);
CREATE INDEX IF NOT EXISTS idx_template_profiles_user_id ON public.template_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_template_profiles_resume_id ON public.template_profiles(resume_id);
CREATE INDEX IF NOT EXISTS idx_job_descriptions_user_id ON public.job_descriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_user_id ON public.pipeline_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_resume_id ON public.pipeline_runs(resume_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status ON public.pipeline_runs(status);
CREATE INDEX IF NOT EXISTS idx_tailoring_results_user_id ON public.tailoring_results(user_id);
CREATE INDEX IF NOT EXISTS idx_tailoring_results_run_id ON public.tailoring_results(run_id);
CREATE INDEX IF NOT EXISTS idx_usage_events_user_id ON public.usage_events(user_id);
CREATE INDEX IF NOT EXISTS idx_master_profile_items_user_id ON public.master_profile_items(user_id);

-- Vector HNSW index for semantic similarity search
CREATE INDEX IF NOT EXISTS idx_master_profile_items_embedding
    ON public.master_profile_items USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- ====================================================================
-- FUNCTIONS & TRIGGERS
-- ====================================================================

-- Trigger to auto-update updated_at timestamps
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = public
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_resumes_updated_at ON public.resumes;
CREATE TRIGGER trg_resumes_updated_at
    BEFORE UPDATE ON public.resumes
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS trg_pipeline_runs_updated_at ON public.pipeline_runs;
CREATE TRIGGER trg_pipeline_runs_updated_at
    BEFORE UPDATE ON public.pipeline_runs
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Trigger on auth.users to create/update public.profiles
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    INSERT INTO public.profiles (id, display_name, created_at)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1)),
        now()
    )
    ON CONFLICT (id) DO UPDATE
    SET display_name = EXCLUDED.display_name;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT OR UPDATE ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Database-Enforced Atomic Optimistic Locking for Resumes
CREATE OR REPLACE FUNCTION public.update_resume_optimistic(
    p_resume_id UUID,
    p_expected_version INT,
    p_title TEXT DEFAULT NULL,
    p_content JSONB DEFAULT NULL,
    p_style JSONB DEFAULT NULL,
    p_template_id TEXT DEFAULT NULL
)
RETURNS public.resumes
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = public
AS $$
DECLARE
    v_updated public.resumes;
    v_current_version INT;
BEGIN
    -- Verify row exists and belongs to current authenticated user
    SELECT version INTO v_current_version
    FROM public.resumes
    WHERE id = p_resume_id AND user_id = (SELECT auth.uid());

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Resume % not found or unauthorized', p_resume_id USING errcode = 'P0002';
    END IF;

    -- Strict version equality check
    IF v_current_version <> p_expected_version THEN
        RAISE EXCEPTION 'Version conflict: expected %, found %', p_expected_version, v_current_version USING errcode = 'P0001';
    END IF;

    -- Atomically update content, style, title, and increment version
    UPDATE public.resumes
    SET
        title = COALESCE(p_title, title),
        content = COALESCE(p_content, content),
        style = COALESCE(p_style, style),
        template_id = COALESCE(p_template_id, template_id),
        version = version + 1,
        updated_at = now()
    WHERE id = p_resume_id
      AND user_id = (SELECT auth.uid())
      AND version = p_expected_version
    RETURNING * INTO v_updated;

    RETURN v_updated;
END;
$$;

-- Stale Pipeline Runs Cleanup Function (marked as failed on backend startup)
CREATE OR REPLACE FUNCTION public.mark_stale_pipeline_runs(p_timeout_minutes INT DEFAULT 15)
RETURNS INT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_count INT;
BEGIN
    UPDATE public.pipeline_runs
    SET
        status = 'failed',
        error = COALESCE(error, 'Run timed out or interrupted by server restart.'),
        updated_at = now()
    WHERE status IN ('queued', 'running')
      AND updated_at < (now() - (p_timeout_minutes || ' minutes')::interval);

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$;

-- Revoke execute on internal security definer functions from public
REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM PUBLIC, anon, authenticated;
REVOKE EXECUTE ON FUNCTION public.mark_stale_pipeline_runs(INT) FROM PUBLIC, anon, authenticated;

-- Grant execute on optimistic update to authenticated users, revoke from anon
GRANT EXECUTE ON FUNCTION public.update_resume_optimistic(UUID, INT, TEXT, JSONB, JSONB, TEXT) TO authenticated;
REVOKE EXECUTE ON FUNCTION public.update_resume_optimistic(UUID, INT, TEXT, JSONB, JSONB, TEXT) FROM anon, PUBLIC;

-- ====================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ====================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resume_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.template_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pipeline_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tailoring_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usage_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.master_profile_items ENABLE ROW LEVEL SECURITY;

-- 1. PROFILES POLICIES
DROP POLICY IF EXISTS "profiles_select_own" ON public.profiles;
CREATE POLICY "profiles_select_own" ON public.profiles
    FOR SELECT TO authenticated
    USING ((SELECT auth.uid()) = id);

DROP POLICY IF EXISTS "profiles_update_own" ON public.profiles;
CREATE POLICY "profiles_update_own" ON public.profiles
    FOR UPDATE TO authenticated
    USING ((SELECT auth.uid()) = id)
    WITH CHECK ((SELECT auth.uid()) = id);

-- 2. RESUMES POLICIES (Full user CRUD, strict WITH CHECK)
DROP POLICY IF EXISTS "resumes_select_own" ON public.resumes;
CREATE POLICY "resumes_select_own" ON public.resumes
    FOR SELECT TO authenticated
    USING ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "resumes_insert_own" ON public.resumes;
CREATE POLICY "resumes_insert_own" ON public.resumes
    FOR INSERT TO authenticated
    WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "resumes_update_own" ON public.resumes;
CREATE POLICY "resumes_update_own" ON public.resumes
    FOR UPDATE TO authenticated
    USING ((SELECT auth.uid()) = user_id)
    WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "resumes_delete_own" ON public.resumes;
CREATE POLICY "resumes_delete_own" ON public.resumes
    FOR DELETE TO authenticated
    USING ((SELECT auth.uid()) = user_id);

-- 3. RESUME FILES POLICIES (Full user CRUD)
DROP POLICY IF EXISTS "resume_files_select_own" ON public.resume_files;
CREATE POLICY "resume_files_select_own" ON public.resume_files
    FOR SELECT TO authenticated
    USING ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "resume_files_insert_own" ON public.resume_files;
CREATE POLICY "resume_files_insert_own" ON public.resume_files
    FOR INSERT TO authenticated
    WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "resume_files_update_own" ON public.resume_files;
CREATE POLICY "resume_files_update_own" ON public.resume_files
    FOR UPDATE TO authenticated
    USING ((SELECT auth.uid()) = user_id)
    WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "resume_files_delete_own" ON public.resume_files;
CREATE POLICY "resume_files_delete_own" ON public.resume_files
    FOR DELETE TO authenticated
    USING ((SELECT auth.uid()) = user_id);

-- 4. JOB DESCRIPTIONS POLICIES (Full user CRUD)
DROP POLICY IF EXISTS "job_descriptions_select_own" ON public.job_descriptions;
CREATE POLICY "job_descriptions_select_own" ON public.job_descriptions
    FOR SELECT TO authenticated
    USING ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "job_descriptions_insert_own" ON public.job_descriptions;
CREATE POLICY "job_descriptions_insert_own" ON public.job_descriptions
    FOR INSERT TO authenticated
    WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "job_descriptions_update_own" ON public.job_descriptions;
CREATE POLICY "job_descriptions_update_own" ON public.job_descriptions
    FOR UPDATE TO authenticated
    USING ((SELECT auth.uid()) = user_id)
    WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "job_descriptions_delete_own" ON public.job_descriptions;
CREATE POLICY "job_descriptions_delete_own" ON public.job_descriptions
    FOR DELETE TO authenticated
    USING ((SELECT auth.uid()) = user_id);

-- 5. MASTER PROFILE ITEMS POLICIES (Full user CRUD)
DROP POLICY IF EXISTS "master_profile_items_select_own" ON public.master_profile_items;
CREATE POLICY "master_profile_items_select_own" ON public.master_profile_items
    FOR SELECT TO authenticated
    USING ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "master_profile_items_insert_own" ON public.master_profile_items;
CREATE POLICY "master_profile_items_insert_own" ON public.master_profile_items
    FOR INSERT TO authenticated
    WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "master_profile_items_update_own" ON public.master_profile_items;
CREATE POLICY "master_profile_items_update_own" ON public.master_profile_items
    FOR UPDATE TO authenticated
    USING ((SELECT auth.uid()) = user_id)
    WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "master_profile_items_delete_own" ON public.master_profile_items;
CREATE POLICY "master_profile_items_delete_own" ON public.master_profile_items
    FOR DELETE TO authenticated
    USING ((SELECT auth.uid()) = user_id);

-- 6. TEMPLATE PROFILES POLICIES (Users get SELECT-only; service role writes)
DROP POLICY IF EXISTS "template_profiles_select_own" ON public.template_profiles;
CREATE POLICY "template_profiles_select_own" ON public.template_profiles
    FOR SELECT TO authenticated
    USING ((SELECT auth.uid()) = user_id);

-- 7. PIPELINE RUNS POLICIES (Users get SELECT-only; service role writes)
DROP POLICY IF EXISTS "pipeline_runs_select_own" ON public.pipeline_runs;
CREATE POLICY "pipeline_runs_select_own" ON public.pipeline_runs
    FOR SELECT TO authenticated
    USING ((SELECT auth.uid()) = user_id);

-- 8. TAILORING RESULTS POLICIES (Users get SELECT-only; service role writes)
DROP POLICY IF EXISTS "tailoring_results_select_own" ON public.tailoring_results;
CREATE POLICY "tailoring_results_select_own" ON public.tailoring_results
    FOR SELECT TO authenticated
    USING ((SELECT auth.uid()) = user_id);

-- 9. USAGE EVENTS POLICIES (Users get SELECT-only; service role writes)
DROP POLICY IF EXISTS "usage_events_select_own" ON public.usage_events;
CREATE POLICY "usage_events_select_own" ON public.usage_events
    FOR SELECT TO authenticated
    USING ((SELECT auth.uid()) = user_id);

-- ====================================================================
-- STORAGE BUCKETS AND STORAGE RLS
-- ====================================================================
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES
    ('originals', 'originals', false, 26214400, ARRAY['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']),
    ('exports', 'exports', false, 26214400, ARRAY['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/png'])
ON CONFLICT (id) DO UPDATE
SET
    public = false,
    file_size_limit = EXCLUDED.file_size_limit,
    allowed_mime_types = EXCLUDED.allowed_mime_types;

-- Storage RLS on storage.objects: {user_id}/{resume_id}/{filename}
DROP POLICY IF EXISTS "storage_select_own" ON storage.objects;
CREATE POLICY "storage_select_own" ON storage.objects
    FOR SELECT TO authenticated
    USING (
        bucket_id IN ('originals', 'exports')
        AND (SELECT auth.uid())::text = (storage.foldername(name))[1]
    );

DROP POLICY IF EXISTS "storage_insert_own" ON storage.objects;
CREATE POLICY "storage_insert_own" ON storage.objects
    FOR INSERT TO authenticated
    WITH CHECK (
        bucket_id IN ('originals', 'exports')
        AND (SELECT auth.uid())::text = (storage.foldername(name))[1]
    );

DROP POLICY IF EXISTS "storage_update_own" ON storage.objects;
CREATE POLICY "storage_update_own" ON storage.objects
    FOR UPDATE TO authenticated
    USING (
        bucket_id IN ('originals', 'exports')
        AND (SELECT auth.uid())::text = (storage.foldername(name))[1]
    )
    WITH CHECK (
        bucket_id IN ('originals', 'exports')
        AND (SELECT auth.uid())::text = (storage.foldername(name))[1]
    );

DROP POLICY IF EXISTS "storage_delete_own" ON storage.objects;
CREATE POLICY "storage_delete_own" ON storage.objects
    FOR DELETE TO authenticated
    USING (
        bucket_id IN ('originals', 'exports')
        AND (SELECT auth.uid())::text = (storage.foldername(name))[1]
    );

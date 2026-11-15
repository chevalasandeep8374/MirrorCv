-- ====================================================================
-- Migration: 20261115180000_phase_d_compositions.sql
-- Description: Phase D Compositions Table (Agent 3 output)
--              Strictly backend-written; users get SELECT-only via RLS.
-- ====================================================================

CREATE TABLE IF NOT EXISTS public.compositions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    resume_id UUID NOT NULL REFERENCES public.resumes(id) ON DELETE CASCADE,
    run_id UUID NOT NULL REFERENCES public.pipeline_runs(id) ON DELETE CASCADE,
    composition_result JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'ready' CHECK (status IN ('ready', 'layout_changed', 'failed')),
    fidelity_score NUMERIC(5, 2) NOT NULL DEFAULT 100.0,
    page_count_before INT NOT NULL DEFAULT 1,
    page_count_after INT NOT NULL DEFAULT 1,
    storage_path_docx TEXT,
    storage_path_pdf TEXT,
    integrity_report JSONB NOT NULL DEFAULT '{}'::jsonb,
    fit_loop JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_compositions_user_id ON public.compositions(user_id);
CREATE INDEX IF NOT EXISTS idx_compositions_resume_id ON public.compositions(resume_id);
CREATE INDEX IF NOT EXISTS idx_compositions_run_id ON public.compositions(run_id);
CREATE INDEX IF NOT EXISTS idx_compositions_status ON public.compositions(status);

-- Enable RLS
ALTER TABLE public.compositions ENABLE ROW LEVEL SECURITY;

-- SELECT-only policy for authenticated users (users can only read their own compositions)
DROP POLICY IF EXISTS "compositions_select_own" ON public.compositions;
CREATE POLICY "compositions_select_own" ON public.compositions
    FOR SELECT TO authenticated
    USING ((SELECT auth.uid()) = user_id);

-- Phase E Security Hardening Migration
-- 1. Ensure public.compositions table exists with SELECT-only RLS
CREATE TABLE IF NOT EXISTS public.compositions (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    resume_id UUID NOT NULL REFERENCES public.resumes(id) ON DELETE CASCADE,
    run_id TEXT NOT NULL,
    composition_result JSONB NOT NULL,
    status TEXT NOT NULL,
    fidelity_score NUMERIC(5, 2) NOT NULL,
    page_count_before INT NOT NULL DEFAULT 1,
    page_count_after INT NOT NULL DEFAULT 1,
    storage_path_docx TEXT,
    storage_path_pdf TEXT,
    integrity_report JSONB NOT NULL DEFAULT '{}'::jsonb,
    fit_loop JSONB NOT NULL DEFAULT '{}'::jsonb,
    user_acknowledged_overflow BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.compositions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "compositions_select_policy" ON public.compositions;
CREATE POLICY "compositions_select_policy" ON public.compositions
    FOR SELECT TO authenticated
    USING ((SELECT auth.uid()) = user_id);

-- 2. Update handle_new_user with search_path = ''
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, created_at, updated_at)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
        now(),
        now()
    );
    RETURN NEW;
END;
$$;

REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM PUBLIC, anon, authenticated;

-- 3. Update mark_stale_pipeline_runs with search_path = ''
CREATE OR REPLACE FUNCTION public.mark_stale_pipeline_runs(timeout_seconds INT DEFAULT 300)
RETURNS INT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
    affected INT;
BEGIN
    UPDATE public.pipeline_runs
    SET status = 'failed',
        current_stage = 'timed_out',
        updated_at = now()
    WHERE status IN ('queued', 'running')
      AND updated_at < (now() - (timeout_seconds || ' seconds')::INTERVAL);
    GET DIAGNOSTICS affected = ROW_COUNT;
    RETURN affected;
END;
$$;

REVOKE EXECUTE ON FUNCTION public.mark_stale_pipeline_runs(INT) FROM PUBLIC, anon, authenticated;

-- 4. Secure create_template_profile: search_path = '' and REVOKE ALL from public/anon/authenticated
CREATE OR REPLACE FUNCTION public.create_template_profile(
    p_id UUID,
    p_user_id UUID,
    p_resume_id UUID,
    p_version INT,
    p_profile JSONB,
    p_slot_map JSONB,
    p_fidelity_score NUMERIC,
    p_status TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
    v_row public.template_profiles%ROWTYPE;
BEGIN
    INSERT INTO public.template_profiles (
        id, user_id, resume_id, version, profile, slot_map, fidelity_score, status, created_at
    ) VALUES (
        p_id, p_user_id, p_resume_id, COALESCE(p_version, 1), p_profile, p_slot_map, p_fidelity_score, COALESCE(p_status, 'ready'), now()
    )
    ON CONFLICT (id) DO UPDATE SET
        profile = EXCLUDED.profile,
        slot_map = EXCLUDED.slot_map,
        fidelity_score = EXCLUDED.fidelity_score,
        status = EXCLUDED.status
    RETURNING * INTO v_row;

    RETURN to_jsonb(v_row);
END;
$$;

REVOKE EXECUTE ON FUNCTION public.create_template_profile(UUID, UUID, UUID, INT, JSONB, JSONB, NUMERIC, TEXT) FROM PUBLIC, anon, authenticated;

-- 5. Secure queue_pipeline_run: search_path = '' and REVOKE ALL from public/anon/authenticated
CREATE OR REPLACE FUNCTION public.queue_pipeline_run(
    p_id UUID,
    p_user_id UUID,
    p_resume_id UUID,
    p_status TEXT DEFAULT 'queued',
    p_current_stage TEXT DEFAULT 'queued',
    p_stage_log JSONB DEFAULT '[]'::jsonb
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
    v_row public.pipeline_runs%ROWTYPE;
BEGIN
    INSERT INTO public.pipeline_runs (
        id, user_id, resume_id, status, current_stage, stage_log, created_at, updated_at
    ) VALUES (
        p_id, p_user_id, p_resume_id, COALESCE(p_status, 'queued'), COALESCE(p_current_stage, 'queued'), p_stage_log, now(), now()
    )
    RETURNING * INTO v_row;

    RETURN to_jsonb(v_row);
END;
$$;

REVOKE EXECUTE ON FUNCTION public.queue_pipeline_run(UUID, UUID, UUID, TEXT, TEXT, JSONB) FROM PUBLIC, anon, authenticated;

-- 6. Secure update_template_slot: search_path = '', enforce auth.uid(), REVOKE from anon
CREATE OR REPLACE FUNCTION public.update_template_slot(
    p_template_profile_id UUID,
    p_slot_id TEXT,
    p_new_role TEXT,
    p_new_binds TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
    v_profile JSONB;
    v_slot_map JSONB;
    v_slots JSONB;
    v_idx INT;
    v_slot JSONB;
    v_updated_slots JSONB := '[]'::jsonb;
    v_found BOOLEAN := false;
    v_row public.template_profiles%ROWTYPE;
    v_caller_id UUID;
BEGIN
    v_caller_id := (SELECT auth.uid());
    IF v_caller_id IS NULL THEN
        RAISE EXCEPTION 'Authentication required';
    END IF;

    SELECT profile, slot_map INTO v_profile, v_slot_map
    FROM public.template_profiles
    WHERE id = p_template_profile_id AND user_id = v_caller_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Template profile not found or access denied';
    END IF;

    v_slots := v_profile->'slots';
    FOR v_idx IN 0 .. jsonb_array_length(v_slots) - 1 LOOP
        v_slot := v_slots->v_idx;
        IF (v_slot->>'slot_id') = p_slot_id THEN
            IF p_new_role IS NOT NULL THEN
                v_slot := jsonb_set(v_slot, '{role}', to_jsonb(p_new_role));
            END IF;
            IF p_new_binds IS NOT NULL THEN
                v_slot := jsonb_set(v_slot, '{binds}', jsonb_build_array(p_new_binds));
            END IF;
            v_found := true;
        END IF;
        v_updated_slots := v_updated_slots || jsonb_build_array(v_slot);
    END LOOP;

    IF NOT v_found THEN
        RAISE EXCEPTION 'Slot % not found in template profile', p_slot_id;
    END IF;

    v_profile := jsonb_set(v_profile, '{slots}', v_updated_slots);

    IF p_new_binds IS NOT NULL AND v_slot_map ? p_slot_id THEN
        v_slot_map := jsonb_set(v_slot_map, ARRAY[p_slot_id, 'target_field'], to_jsonb(p_new_binds));
    END IF;

    UPDATE public.template_profiles
    SET profile = v_profile, slot_map = v_slot_map
    WHERE id = p_template_profile_id AND user_id = v_caller_id
    RETURNING * INTO v_row;

    RETURN to_jsonb(v_row);
END;
$$;

-- Drop old overload that accepted p_user_id as argument
DROP FUNCTION IF EXISTS public.update_template_slot(UUID, UUID, TEXT, TEXT, TEXT);

REVOKE EXECUTE ON FUNCTION public.update_template_slot(UUID, TEXT, TEXT, TEXT) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.update_template_slot(UUID, TEXT, TEXT, TEXT) TO authenticated;

-- 7. Fix match_master_profile_items: search_path = '', enforce auth.uid(), REVOKE from anon
CREATE OR REPLACE FUNCTION public.match_master_profile_items(
    query_embedding public.vector(1536),
    match_threshold DOUBLE PRECISION DEFAULT 0.65,
    match_count INTEGER DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    type TEXT,
    text TEXT,
    metadata JSONB,
    similarity DOUBLE PRECISION
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
    v_caller_id UUID;
BEGIN
    v_caller_id := (SELECT auth.uid());
    IF v_caller_id IS NULL THEN
        RAISE EXCEPTION 'Authentication required';
    END IF;

    RETURN QUERY
    SELECT
        mpi.id,
        mpi.type,
        mpi.text,
        mpi.metadata,
        (1 - (mpi.embedding operator(public.<=>) query_embedding))::DOUBLE PRECISION AS similarity
    FROM public.master_profile_items mpi
    WHERE mpi.user_id = v_caller_id
      AND mpi.embedding IS NOT NULL
      AND (1 - (mpi.embedding operator(public.<=>) query_embedding)) >= match_threshold
    ORDER BY mpi.embedding operator(public.<=>) query_embedding ASC
    LIMIT match_count;
END;
$$;

-- Drop old overload that accepted p_user_id
DROP FUNCTION IF EXISTS public.match_master_profile_items(UUID, public.vector, DOUBLE PRECISION, INTEGER);

REVOKE EXECUTE ON FUNCTION public.match_master_profile_items(public.vector(1536), DOUBLE PRECISION, INTEGER) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.match_master_profile_items(public.vector(1536), DOUBLE PRECISION, INTEGER) TO authenticated;

-- 8. Fix match_skill_taxonomy: search_path = '', revoke from anon, grant to authenticated
CREATE OR REPLACE FUNCTION public.match_skill_taxonomy(
    query_embedding public.vector(1536),
    match_threshold DOUBLE PRECISION DEFAULT 0.75,
    match_count INTEGER DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    canonical_name TEXT,
    aliases TEXT[],
    category TEXT,
    role_families TEXT[],
    status TEXT,
    similarity DOUBLE PRECISION
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    RETURN QUERY
    SELECT
        st.id,
        st.canonical_name,
        st.aliases,
        st.category,
        st.role_families,
        st.status,
        (1 - (st.embedding operator(public.<=>) query_embedding))::DOUBLE PRECISION AS similarity
    FROM public.skill_taxonomy st
    WHERE st.status = 'approved'
      AND st.embedding IS NOT NULL
      AND (1 - (st.embedding operator(public.<=>) query_embedding)) >= match_threshold
    ORDER BY st.embedding operator(public.<=>) query_embedding ASC
    LIMIT match_count;
END;
$$;

REVOKE EXECUTE ON FUNCTION public.match_skill_taxonomy(public.vector(1536), DOUBLE PRECISION, INTEGER) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.match_skill_taxonomy(public.vector(1536), DOUBLE PRECISION, INTEGER) TO authenticated;

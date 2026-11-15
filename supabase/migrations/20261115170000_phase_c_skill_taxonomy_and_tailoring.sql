-- Phase C: Skill Taxonomy, Job Description Hashing, and Vector Matching RPCs

-- 1. Skill Taxonomy Table (read-only for users, writes via backend / service role)
CREATE TABLE IF NOT EXISTS public.skill_taxonomy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_name TEXT NOT NULL UNIQUE,
    aliases TEXT[] NOT NULL DEFAULT '{}',
    category TEXT NOT NULL,
    role_families TEXT[] NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'approved' CHECK (status IN ('candidate', 'approved')),
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.skill_taxonomy ENABLE ROW LEVEL SECURITY;

-- Allow SELECT for all authenticated and anon users (read-only global catalog)
DROP POLICY IF EXISTS "skill_taxonomy_select" ON public.skill_taxonomy;
CREATE POLICY "skill_taxonomy_select" ON public.skill_taxonomy
    FOR SELECT USING (true);

-- Indexes for lightning-fast matching and filtering
CREATE UNIQUE INDEX IF NOT EXISTS idx_skill_taxonomy_canonical_lower 
    ON public.skill_taxonomy(lower(canonical_name));
CREATE INDEX IF NOT EXISTS idx_skill_taxonomy_aliases_gin 
    ON public.skill_taxonomy USING gin(aliases);
CREATE INDEX IF NOT EXISTS idx_skill_taxonomy_status 
    ON public.skill_taxonomy(status);
CREATE INDEX IF NOT EXISTS idx_skill_taxonomy_category 
    ON public.skill_taxonomy(category);
CREATE INDEX IF NOT EXISTS idx_skill_taxonomy_embedding 
    ON public.skill_taxonomy USING hnsw (embedding vector_cosine_ops);

-- 2. Add text_hash column to job_descriptions for caching analyses
ALTER TABLE public.job_descriptions 
    ADD COLUMN IF NOT EXISTS text_hash TEXT;

CREATE INDEX IF NOT EXISTS idx_job_descriptions_user_hash 
    ON public.job_descriptions(user_id, text_hash);

-- 3. Vector Search RPC: Match Approved Skill Taxonomy
CREATE OR REPLACE FUNCTION public.match_skill_taxonomy(
    query_embedding VECTOR(1536),
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
SET search_path = public, extensions
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
        1 - (st.embedding <=> query_embedding) AS similarity
    FROM public.skill_taxonomy st
    WHERE st.status = 'approved'
      AND st.embedding IS NOT NULL
      AND (1 - (st.embedding <=> query_embedding)) >= match_threshold
    ORDER BY st.embedding <=> query_embedding ASC
    LIMIT match_count;
END;
$$;

-- 4. Vector Search RPC: Match User Master Profile Items
CREATE OR REPLACE FUNCTION public.match_master_profile_items(
    p_user_id UUID,
    query_embedding VECTOR(1536),
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
SET search_path = public, extensions
AS $$
BEGIN
    RETURN QUERY
    SELECT
        mpi.id,
        mpi.type,
        mpi.text,
        mpi.metadata,
        1 - (mpi.embedding <=> query_embedding) AS similarity
    FROM public.master_profile_items mpi
    WHERE mpi.user_id = p_user_id
      AND mpi.embedding IS NOT NULL
      AND (1 - (mpi.embedding <=> query_embedding)) >= match_threshold
    ORDER BY mpi.embedding <=> query_embedding ASC
    LIMIT match_count;
END;
$$;

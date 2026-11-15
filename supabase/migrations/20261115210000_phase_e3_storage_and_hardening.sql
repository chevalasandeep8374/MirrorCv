-- Phase E3: Storage Policies Lockdown, GoTrue User Trigger Hardening, and Migration Parity
-- Enforces:
-- 1. storage 'exports' bucket is backend-writable only (users SELECT only; no user INSERT/UPDATE/DELETE).
-- 2. storage 'originals' bucket remains user-writable.
-- 3. public.handle_new_user() runs with SET search_path = '' and handles profiles without schema errors.
-- 4. public.pipeline_runs permits INSERT to authenticated users for their own rows (auth.uid() = user_id).
-- 5. RPC privileges are revoked from PUBLIC and anon.

-- 1. Profiles & Auth Trigger Hardening
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    INSERT INTO public.profiles (id, created_at, updated_at)
    VALUES (NEW.id, now(), now())
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 2. Storage Buckets Existence Verification
INSERT INTO storage.buckets (id, name, public)
VALUES ('originals', 'originals', false)
ON CONFLICT (id) DO NOTHING;

INSERT INTO storage.buckets (id, name, public)
VALUES ('exports', 'exports', false)
ON CONFLICT (id) DO NOTHING;

-- 3. Storage Policies Lockdown (Exports writable by backend only, select allowed for owner)
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "storage_insert_own" ON storage.objects;
DROP POLICY IF EXISTS "storage_update_own" ON storage.objects;
DROP POLICY IF EXISTS "storage_delete_own" ON storage.objects;
DROP POLICY IF EXISTS "storage_select_own" ON storage.objects;

-- User can ONLY insert into 'originals', strictly prohibited from 'exports'
CREATE POLICY "storage_insert_own" ON storage.objects
FOR INSERT TO authenticated
WITH CHECK (
    bucket_id = 'originals' AND
    auth.uid()::text = (storage.foldername(name))[1]
);

-- User can ONLY update in 'originals'
CREATE POLICY "storage_update_own" ON storage.objects
FOR UPDATE TO authenticated
USING (
    bucket_id = 'originals' AND
    auth.uid()::text = (storage.foldername(name))[1]
)
WITH CHECK (
    bucket_id = 'originals' AND
    auth.uid()::text = (storage.foldername(name))[1]
);

-- User can ONLY delete from 'originals'
CREATE POLICY "storage_delete_own" ON storage.objects
FOR DELETE TO authenticated
USING (
    bucket_id = 'originals' AND
    auth.uid()::text = (storage.foldername(name))[1]
);

-- User can SELECT from both 'originals' and 'exports' within their own folder
CREATE POLICY "storage_select_own" ON storage.objects
FOR SELECT TO authenticated
USING (
    bucket_id IN ('originals', 'exports') AND
    auth.uid()::text = (storage.foldername(name))[1]
);

-- Backend-authorized worker policies for 'exports'
DROP POLICY IF EXISTS "storage_backend_insert_export" ON storage.objects;
CREATE POLICY "storage_backend_insert_export" ON storage.objects
FOR INSERT TO authenticated
WITH CHECK (
    bucket_id = 'exports' AND
    (current_setting('request.headers', true)::json->>'x-mirrorcv-role') = 'backend_worker' AND
    auth.uid()::text = (storage.foldername(name))[1]
);

DROP POLICY IF EXISTS "storage_backend_delete_export" ON storage.objects;
CREATE POLICY "storage_backend_delete_export" ON storage.objects
FOR DELETE TO authenticated
USING (
    bucket_id = 'exports' AND
    (current_setting('request.headers', true)::json->>'x-mirrorcv-role') = 'backend_worker' AND
    auth.uid()::text = (storage.foldername(name))[1]
);

-- 4. Pipeline Runs RLS Policy
DROP POLICY IF EXISTS "pipeline_runs_insert_own" ON public.pipeline_runs;
CREATE POLICY "pipeline_runs_insert_own" ON public.pipeline_runs
FOR INSERT TO authenticated
WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "pipeline_runs_update_own" ON public.pipeline_runs;
CREATE POLICY "pipeline_runs_update_own" ON public.pipeline_runs
FOR UPDATE TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "pipeline_runs_delete_own" ON public.pipeline_runs;
CREATE POLICY "pipeline_runs_delete_own" ON public.pipeline_runs
FOR DELETE TO authenticated
USING (auth.uid() = user_id);

-- 5. Tailoring Results Schema and RLS Policies
ALTER TABLE public.tailoring_results ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT now();

DROP POLICY IF EXISTS "tailoring_results_insert_own" ON public.tailoring_results;
CREATE POLICY "tailoring_results_insert_own" ON public.tailoring_results
FOR INSERT TO authenticated
WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "tailoring_results_update_own" ON public.tailoring_results;
CREATE POLICY "tailoring_results_update_own" ON public.tailoring_results
FOR UPDATE TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "tailoring_results_delete_own" ON public.tailoring_results;
CREATE POLICY "tailoring_results_delete_own" ON public.tailoring_results
FOR DELETE TO authenticated
USING (auth.uid() = user_id);

-- 6. Compositions RLS Policies
DROP POLICY IF EXISTS "compositions_insert_policy" ON public.compositions;
CREATE POLICY "compositions_insert_policy" ON public.compositions
FOR INSERT TO authenticated
WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "compositions_update_policy" ON public.compositions;
CREATE POLICY "compositions_update_policy" ON public.compositions
FOR UPDATE TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "compositions_delete_policy" ON public.compositions;
CREATE POLICY "compositions_delete_policy" ON public.compositions
FOR DELETE TO authenticated
USING (auth.uid() = user_id);

-- 7. Template Profiles DELETE Policy
DROP POLICY IF EXISTS "template_profiles_delete_own" ON public.template_profiles;
CREATE POLICY "template_profiles_delete_own" ON public.template_profiles
FOR DELETE TO authenticated
USING (auth.uid() = user_id);

-- 8. Revoke sensitive RPCs from PUBLIC and anon
REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM PUBLIC, anon;

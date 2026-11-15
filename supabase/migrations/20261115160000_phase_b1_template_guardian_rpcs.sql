-- Migration: Phase B1 Template Guardian RPCs
-- Allows secure creation and slot editing for template_profiles

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
SET search_path = public
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

CREATE OR REPLACE FUNCTION public.update_template_slot(
    p_template_profile_id UUID,
    p_user_id UUID,
    p_slot_id TEXT,
    p_new_role TEXT,
    p_new_binds TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
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
BEGIN
    SELECT profile, slot_map INTO v_profile, v_slot_map
    FROM public.template_profiles
    WHERE id = p_template_profile_id AND user_id = p_user_id;

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
    WHERE id = p_template_profile_id AND user_id = p_user_id
    RETURNING * INTO v_row;

    RETURN to_jsonb(v_row);
END;
$$;

GRANT EXECUTE ON FUNCTION public.create_template_profile(UUID, UUID, UUID, INT, JSONB, JSONB, NUMERIC, TEXT) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION public.update_template_slot(UUID, UUID, TEXT, TEXT, TEXT) TO authenticated, anon;

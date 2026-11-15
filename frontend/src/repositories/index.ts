import { ResumeRepository } from './ResumeRepository';
import { LocalStorageRepository } from './LocalStorageRepository';
import { SupabaseRepository } from './SupabaseRepository';
import { supabase } from '@/lib/supabase';

export * from './ResumeRepository';
export * from './LocalStorageRepository';
export * from './SupabaseRepository';

// Singletons
export const localRepo = new LocalStorageRepository();
export const supabaseRepo = new SupabaseRepository();

/**
 * Returns the appropriate repository based on authentication state.
 * If user is authenticated with Supabase, returns SupabaseRepository.
 * Otherwise returns LocalStorageRepository as fallback for demo mode.
 */
export async function getActiveRepository(): Promise<ResumeRepository> {
  try {
    const { data } = await supabase.auth.getSession();
    if (data?.session?.user) {
      return supabaseRepo;
    }
  } catch (e) {
    console.warn('Session check fallback to local storage:', e);
  }
  return localRepo;
}

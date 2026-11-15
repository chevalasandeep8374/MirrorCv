import { supabase } from '@/lib/supabase';
import { Resume, ResumeSummary, ResumeUpdatePayload } from '@/types/resume';
import { ResumeRepository, VersionConflictError, ImportResult } from './ResumeRepository';
import { defaultResumeContent, classicSingleColumnPreset } from '@/lib/presets';

interface DbResumeRow {
  id: string;
  user_id: string;
  title: string;
  content: unknown;
  style: unknown;
  template_id: string;
  version: number;
  source_type: 'editor' | 'uploaded_docx' | 'uploaded_pdf';
  is_archived?: boolean;
  tags?: string[];
  folder?: string | null;
  target_job_title?: string | null;
  created_at: string;
  updated_at: string;
}

export class SupabaseRepository implements ResumeRepository {
  private mapRowToResume(row: DbResumeRow): Resume {
    return {
      id: row.id,
      userId: row.user_id,
      title: row.title,
      content: (row.content as Resume['content']) || defaultResumeContent,
      style: (row.style as Resume['style']) || classicSingleColumnPreset,
      templateId: row.template_id || 'classic_single_column',
      version: row.version || 1,
      sourceType: row.source_type || 'editor',
      isArchived: Boolean(row.is_archived),
      tags: row.tags || [],
      folder: row.folder || null,
      targetJobTitle: row.target_job_title || null,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
    };
  }

  private mapRowToSummary(row: DbResumeRow): ResumeSummary {
    return {
      id: row.id,
      userId: row.user_id,
      user_id: row.user_id,
      title: row.title,
      docType: 'resume',
      doc_type: 'resume',
      targetJobTitle: row.target_job_title || null,
      target_job_title: row.target_job_title || null,
      tags: row.tags || [],
      folder: row.folder || null,
      isArchived: Boolean(row.is_archived),
      is_archived: Boolean(row.is_archived),
      version: row.version || 1,
      templateId: row.template_id || 'classic_single_column',
      template_id: row.template_id || 'classic_single_column',
      tailoredFromId: null,
      tailored_from_id: null,
      tailoredFromTitle: null,
      tailored_from_title: null,
      thumbnailPath: null,
      thumbnail_path: null,
      createdAt: row.created_at,
      created_at: row.created_at,
      updatedAt: row.updated_at,
      updated_at: row.updated_at,
    };
  }

  async list(isArchived = false): Promise<ResumeSummary[]> {
    const { data, error } = await supabase
      .from('resumes')
      .select('id, user_id, title, template_id, version, source_type, is_archived, tags, folder, target_job_title, created_at, updated_at')
      .eq('is_archived', isArchived)
      .order('updated_at', { ascending: false });

    if (error) {
      console.error('Supabase list resumes error:', error);
      throw new Error(`Failed to list resumes: ${error.message}`);
    }

    return ((data || []) as DbResumeRow[]).map((r) => this.mapRowToSummary(r));
  }

  async get(id: string): Promise<Resume> {
    const { data, error } = await supabase
      .from('resumes')
      .select('*')
      .eq('id', id)
      .single();

    if (error || !data) {
      console.error(`Supabase get resume '${id}' error:`, error);
      throw new Error(`Resume '${id}' not found: ${error?.message || 'No record'}`);
    }

    return this.mapRowToResume(data as DbResumeRow);
  }

  async create(initial?: Partial<Resume>): Promise<Resume> {
    const { data: userData, error: userError } = await supabase.auth.getUser();
    if (userError || !userData?.user) {
      throw new Error('User must be authenticated to create a resume in cloud storage.');
    }

    const payload = {
      user_id: userData.user.id,
      title: initial?.title || 'Untitled Resume',
      content: initial?.content || defaultResumeContent,
      style: initial?.style || classicSingleColumnPreset,
      template_id: initial?.templateId || initial?.style?.templateId || 'classic_single_column',
      version: 1,
      source_type: initial?.sourceType || 'editor',
      tags: initial?.tags || [],
      folder: initial?.folder || null,
      target_job_title: initial?.targetJobTitle || null,
    };

    const { data, error } = await supabase
      .from('resumes')
      .insert(payload)
      .select()
      .single();

    if (error || !data) {
      throw new Error(`Failed to create resume: ${error?.message}`);
    }

    return this.mapRowToResume(data as DbResumeRow);
  }

  async update(id: string, payload: ResumeUpdatePayload, expectedVersion?: number): Promise<Resume> {
    const targetExpectedVersion = expectedVersion !== undefined ? expectedVersion : payload.expected_version;

    // If expectedVersion is provided, use atomic optimistic locking RPC function
    if (targetExpectedVersion !== undefined) {
      const { data, error } = await supabase.rpc('update_resume_optimistic', {
        p_resume_id: id,
        p_expected_version: targetExpectedVersion,
        p_title: payload.title || null,
        p_content: payload.content || null,
        p_style: payload.style || null,
        p_template_id: payload.templateId || payload.template_id || null,
      });

      if (error) {
        if (error.code === 'P0001' || error.message.includes('Version conflict')) {
          throw new VersionConflictError(
            `Resume has been updated in another window. (Expected: ${targetExpectedVersion})`,
            targetExpectedVersion
          );
        }
        throw new Error(`Optimistic update error: ${error.message}`);
      }

      return this.mapRowToResume(data as DbResumeRow);
    }

    // Direct update fallback (increments version automatically)
    const updateObj: Record<string, unknown> = {
      updated_at: new Date().toISOString(),
    };
    if (payload.title !== undefined) updateObj.title = payload.title;
    if (payload.content !== undefined) updateObj.content = payload.content;
    if (payload.style !== undefined) updateObj.style = payload.style;
    if (payload.templateId !== undefined) updateObj.template_id = payload.templateId;

    const { data, error } = await supabase
      .from('resumes')
      .update(updateObj)
      .eq('id', id)
      .select()
      .single();

    if (error || !data) {
      throw new Error(`Failed to update resume: ${error?.message}`);
    }

    return this.mapRowToResume(data as DbResumeRow);
  }

  async patch(id: string, patch: Partial<ResumeSummary>): Promise<ResumeSummary> {
    const updateObj: Record<string, unknown> = {
      updated_at: new Date().toISOString(),
    };
    if (patch.title !== undefined) updateObj.title = patch.title;
    if (patch.folder !== undefined) updateObj.folder = patch.folder;
    if (patch.tags !== undefined) updateObj.tags = patch.tags;
    if (patch.targetJobTitle !== undefined) updateObj.target_job_title = patch.targetJobTitle;
    if (patch.isArchived !== undefined) updateObj.is_archived = patch.isArchived;

    const { data, error } = await supabase
      .from('resumes')
      .update(updateObj)
      .eq('id', id)
      .select()
      .single();

    if (error || !data) {
      throw new Error(`Failed to patch resume: ${error?.message}`);
    }

    return this.mapRowToSummary(data as DbResumeRow);
  }

  async duplicate(id: string): Promise<Resume> {
    const original = await this.get(id);
    return this.create({
      title: `${original.title} (Copy)`,
      content: original.content,
      style: original.style,
      templateId: original.templateId,
      sourceType: original.sourceType,
      tags: original.tags,
      folder: original.folder,
      targetJobTitle: original.targetJobTitle,
    });
  }

  async delete(id: string): Promise<void> {
    const { error } = await supabase.from('resumes').delete().eq('id', id);
    if (error) {
      throw new Error(`Failed to delete resume: ${error.message}`);
    }
  }

  /**
   * Idempotent import of local resumes to Supabase.
   * Ensures identical items are not duplicated when imported multiple times.
   */
  async importLocalResumes(localResumes: Resume[]): Promise<ImportResult> {
    const { data: userData, error: userError } = await supabase.auth.getUser();
    if (userError || !userData?.user) {
      throw new Error('User must be logged in to import local resumes.');
    }

    const userId = userData.user.id;
    let importedCount = 0;
    let skippedCount = 0;
    const errors: string[] = [];

    // Fetch existing cloud resumes for this user to check idempotency
    const { data: existingCloud } = await supabase
      .from('resumes')
      .select('id, title');
    const existingIds = new Set((existingCloud || []).map((r) => r.id));
    const existingTitles = new Set((existingCloud || []).map((r) => r.title));

    for (const resume of localResumes) {
      try {
        // Idempotency check: Skip if exact ID or duplicate title already exists
        if (existingIds.has(resume.id) || existingTitles.has(resume.title)) {
          skippedCount++;
          continue;
        }

        const payload = {
          id: resume.id.includes('-') && resume.id.length >= 32 ? resume.id : undefined,
          user_id: userId,
          title: resume.title,
          content: resume.content || defaultResumeContent,
          style: resume.style || classicSingleColumnPreset,
          template_id: resume.templateId || 'classic_single_column',
          version: resume.version || 1,
          source_type: resume.sourceType || 'editor',
          tags: resume.tags || [],
          folder: resume.folder || null,
          target_job_title: resume.targetJobTitle || null,
        };

        const { error } = await supabase.from('resumes').insert(payload);
        if (error) {
          errors.push(`Failed to import '${resume.title}': ${error.message}`);
        } else {
          importedCount++;
          existingTitles.add(resume.title);
        }
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        errors.push(`Error importing '${resume.title}': ${msg}`);
      }
    }

    return { importedCount, skippedCount, errors };
  }
}

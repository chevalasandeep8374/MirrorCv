import { Resume, ResumeSummary, ResumeUpdatePayload } from '@/types/resume';
import { ResumeRepository, VersionConflictError } from './ResumeRepository';
import { defaultResumeContent, classicSingleColumnPreset } from '@/lib/presets';

const STORAGE_KEY = 'mirrorcv_local_resumes_v1';

export class LocalStorageRepository implements ResumeRepository {
  private isBrowser(): boolean {
    return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';
  }

  private readStorage(): Record<string, Resume> {
    if (!this.isBrowser()) return {};
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (!raw) return {};
      return JSON.parse(raw);
    } catch (e) {
      console.warn('Failed to parse local storage resumes:', e);
      return {};
    }
  }

  private writeStorage(data: Record<string, Resume>): void {
    if (!this.isBrowser()) return;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) {
      console.error('Failed to write local storage resumes:', e);
    }
  }

  async list(isArchived = false): Promise<ResumeSummary[]> {
    const data = this.readStorage();
    const list = Object.values(data).filter((r) => Boolean(r.isArchived) === isArchived);

    return list
      .map((r) => ({
        id: r.id,
        userId: r.userId || 'demo_local_user',
        user_id: r.userId || 'demo_local_user',
        title: r.title,
        docType: 'resume',
        doc_type: 'resume',
        targetJobTitle: r.targetJobTitle || null,
        target_job_title: r.targetJobTitle || null,
        tags: r.tags || [],
        folder: r.folder || null,
        isArchived: Boolean(r.isArchived),
        is_archived: Boolean(r.isArchived),
        version: r.version || 1,
        templateId: r.templateId || r.style?.templateId || 'classic_single_column',
        template_id: r.templateId || r.style?.templateId || 'classic_single_column',
        tailoredFromId: null,
        tailored_from_id: null,
        tailoredFromTitle: null,
        tailored_from_title: null,
        thumbnailPath: null,
        thumbnail_path: null,
        createdAt: r.createdAt,
        created_at: r.createdAt,
        updatedAt: r.updatedAt,
        updated_at: r.updatedAt,
      }))
      .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
  }

  async get(id: string): Promise<Resume> {
    const data = this.readStorage();
    const resume = data[id];
    if (resume) return resume;

    // If demo or empty, return default seeded resume
    const now = new Date().toISOString();
    const demo: Resume = {
      id: id || 'local_demo',
      userId: 'demo_local_user',
      title: 'Demo Resume',
      content: defaultResumeContent,
      style: classicSingleColumnPreset,
      templateId: 'classic_single_column',
      version: 1,
      sourceType: 'editor',
      isArchived: false,
      tags: ['demo'],
      createdAt: now,
      updatedAt: now,
    };
    data[demo.id] = demo;
    this.writeStorage(data);
    return demo;
  }

  async create(initial?: Partial<Resume>): Promise<Resume> {
    const data = this.readStorage();
    const now = new Date().toISOString();
    const id = initial?.id || (typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : `local_${Date.now()}`);

    const newResume: Resume = {
      id,
      userId: initial?.userId || 'demo_local_user',
      title: initial?.title || 'Untitled Resume',
      content: initial?.content || defaultResumeContent,
      style: initial?.style || classicSingleColumnPreset,
      templateId: initial?.templateId || initial?.style?.templateId || 'classic_single_column',
      version: 1,
      sourceType: initial?.sourceType || 'editor',
      isArchived: false,
      tags: initial?.tags || [],
      folder: initial?.folder || null,
      targetJobTitle: initial?.targetJobTitle || null,
      createdAt: now,
      updatedAt: now,
    };

    data[id] = newResume;
    this.writeStorage(data);
    return newResume;
  }

  async update(id: string, payload: ResumeUpdatePayload, expectedVersion?: number): Promise<Resume> {
    const data = this.readStorage();
    const existing = data[id];
    if (!existing) {
      throw new Error(`Local resume '${id}' not found`);
    }

    const currentVersion = existing.version || 1;
    const expVer = expectedVersion !== undefined ? expectedVersion : payload.expected_version;
    if (expVer !== undefined && expVer !== currentVersion) {
      throw new VersionConflictError(
        `Version conflict: expected version ${expVer}, but found ${currentVersion}`,
        expVer,
        currentVersion
      );
    }

    const updated: Resume = {
      ...existing,
      title: payload.title !== undefined ? payload.title : existing.title,
      content: payload.content !== undefined ? payload.content : existing.content,
      style: payload.style !== undefined ? payload.style : existing.style,
      templateId: payload.templateId !== undefined ? payload.templateId : existing.templateId,
      version: currentVersion + 1,
      updatedAt: new Date().toISOString(),
    };

    data[id] = updated;
    this.writeStorage(data);
    return updated;
  }

  async patch(id: string, patch: Partial<ResumeSummary>): Promise<ResumeSummary> {
    const data = this.readStorage();
    const existing = data[id];
    if (!existing) {
      throw new Error(`Local resume '${id}' not found`);
    }

    const updated: Resume = {
      ...existing,
      title: patch.title !== undefined ? patch.title : existing.title,
      folder: patch.folder !== undefined ? patch.folder : existing.folder,
      tags: patch.tags !== undefined ? patch.tags : existing.tags,
      targetJobTitle: patch.targetJobTitle !== undefined ? patch.targetJobTitle : existing.targetJobTitle,
      isArchived: patch.isArchived !== undefined ? patch.isArchived : existing.isArchived,
      updatedAt: new Date().toISOString(),
    };

    data[id] = updated;
    this.writeStorage(data);

    return {
      id: updated.id,
      userId: updated.userId,
      title: updated.title,
      docType: 'resume',
      targetJobTitle: updated.targetJobTitle || null,
      tags: updated.tags || [],
      folder: updated.folder || null,
      isArchived: Boolean(updated.isArchived),
      version: updated.version,
      templateId: updated.templateId,
      tailoredFromId: null,
      tailoredFromTitle: null,
      thumbnailPath: null,
      createdAt: updated.createdAt,
      updatedAt: updated.updatedAt,
    };
  }

  async duplicate(id: string): Promise<Resume> {
    const data = this.readStorage();
    const existing = data[id];
    if (!existing) {
      throw new Error(`Resume '${id}' not found`);
    }

    const newId = typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : `local_${Date.now()}`;
    const now = new Date().toISOString();

    const duplicated: Resume = {
      ...existing,
      id: newId,
      title: `${existing.title} (Copy)`,
      version: 1,
      createdAt: now,
      updatedAt: now,
    };

    data[newId] = duplicated;
    this.writeStorage(data);
    return duplicated;
  }

  async delete(id: string): Promise<void> {
    const data = this.readStorage();
    delete data[id];
    this.writeStorage(data);
  }

  /**
   * Helper to check if any resumes exist locally
   */
  hasResumes(): boolean {
    return this.getAll().length > 0;
  }

  /**
   * Helper to retrieve all locally stored resumes for migration
   */
  getAll(): Resume[] {
    const data = this.readStorage();
    return Object.values(data);
  }

  /**
   * Clear local resumes after confirmed migration
   */
  clear(): void {
    if (!this.isBrowser()) return;
    window.localStorage.removeItem(STORAGE_KEY);
  }
}

import { Resume, ResumeSummary, ResumeUpdatePayload } from '@/types/resume';

export interface ImportResult {
  importedCount: number;
  skippedCount: number;
  errors: string[];
}

export interface ResumeRepository {
  /**
   * List all resumes for the current context (or local store), filtered by archive status.
   */
  list(isArchived?: boolean): Promise<ResumeSummary[]>;

  /**
   * Fetch a single resume by its ID.
   */
  get(id: string): Promise<Resume>;

  /**
   * Create a new resume.
   */
  create(initial?: Partial<Resume>): Promise<Resume>;

  /**
   * Update resume title, content, style, or template with optimistic locking.
   * If expectedVersion is provided, the database or local storage enforces that
   * the current version matches expectedVersion, atomically incrementing it to expectedVersion + 1.
   * If there is a mismatch, it throws a VersionConflictError.
   */
  update(id: string, data: ResumeUpdatePayload, expectedVersion?: number): Promise<Resume>;

  /**
   * Partially patch resume metadata (title, folder, tags, isArchived).
   */
  patch(id: string, patch: Partial<ResumeSummary>): Promise<ResumeSummary>;

  /**
   * Duplicate an existing resume.
   */
  duplicate(id: string): Promise<Resume>;

  /**
   * Delete a resume by ID.
   */
  delete(id: string): Promise<void>;

  /**
   * Idempotent import of local resumes to cloud storage.
   * Keeps local copies intact until confirmed.
   */
  importLocalResumes?(localResumes: Resume[]): Promise<ImportResult>;
}

export class VersionConflictError extends Error {
  public expectedVersion: number;
  public actualVersion?: number;

  constructor(message: string, expectedVersion: number, actualVersion?: number) {
    super(message);
    this.name = 'VersionConflictError';
    this.expectedVersion = expectedVersion;
    this.actualVersion = actualVersion;
  }
}

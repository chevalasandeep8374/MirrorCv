/**
 * CompositionResult type definitions for Phase D: Agent 3 (Composer)
 * Matches contracts/schemas/composition_result.schema.json (1.1.0)
 */

export type CompositionSchemaVersion = '1.0.0' | '1.1.0';

export type OutputFileKind = 'original' | 'tailored' | 'export';
export type OutputFileFormat = 'pdf' | 'docx';

export interface OutputFileRef {
  kind: OutputFileKind;
  format?: OutputFileFormat;
  storage_path: string;
  mime_type: string;
  size_bytes: number;
  download_url?: string;
}

export interface OverflowReport {
  has_overflow: boolean;
  overflowing_slots: string[];
  details: string;
}

export interface InvariantCheck {
  name: string;
  passed: boolean;
  details: string;
}

export interface IntegrityReport {
  passed: boolean;
  violations: string[];
  invariants_checked: InvariantCheck[];
  byte_identical_parts?: string[];
  id_collisions_found?: number;
}

export interface FitLoopRound {
  round: number;
  overflowing_slots: string[];
  shortened_changes: string[];
  page_count?: number;
}

export interface FitLoop {
  rounds_executed: number;
  overflow_resolved: boolean;
  history: FitLoopRound[];
}

export interface PerSlotLineCount {
  max_lines: number;
  lines_before?: number;
  lines_after?: number;
  clipped?: boolean;
}

export type CompositionStatus = 'ready' | 'layout_changed' | 'failed' | 'success' | 'warning';

export interface CompositionResult {
  schema_version: CompositionSchemaVersion;
  run_id: string;
  resume_id: string;
  composition_id?: string;
  output_files: OutputFileRef[];
  fidelity_score: number;
  page_count_before?: number;
  page_count_after?: number;
  page_count_preserved?: boolean;
  integrity_report?: IntegrityReport;
  fit_loop?: FitLoop;
  per_slot_lines?: Record<string, PerSlotLineCount>;
  overflow_report: OverflowReport;
  final_content?: Record<string, unknown>;
  substituted_fonts?: string[];
  whitespace_created_pt?: number;
  warnings: string[];
  status: CompositionStatus;
}

/**
 * Updated for Phase B1: contracts/schemas/template_profile.schema.json (1.1.0)
 */

export type SchemaVersion = '1.0.0' | '1.1.0';

export type TemplateSourceType = 'uploaded_docx' | 'uploaded_pdf' | 'editor';

export type TextSlotRole =
  | 'name'
  | 'headline'
  | 'contact'
  | 'section_heading'
  | 'heading'
  | 'item_title'
  | 'item_meta'
  | 'bullet'
  | 'body'
  | 'skill_line'
  | 'link_line'
  | 'separator'
  | 'other';

export type PointerType =
  | 'docx_paragraph'
  | 'docx_table_cell'
  | 'docx_textbox'
  | 'pdf_block'
  | 'editor_path';

export interface SourcePointer {
  pointer_type: PointerType;
  paragraph_index?: number;
  table_path?: number[];
  textbox_id?: string | null;
  page_number?: number;
  bbox?: [number, number, number, number];
}

export interface RunFormatting {
  font_family?: string;
  font_size_pt?: number;
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
  color_hex?: string | null;
  spacing_twips?: number;
}

export interface RunStructure {
  normal_rPr: RunFormatting;
  bold_rPr?: RunFormatting | null;
  italic_rPr?: RunFormatting | null;
}

export interface SlotHyperlink {
  target: string;
  text: string;
}

export interface SlotTab {
  pos_pt: number;
  align: string;
}

export interface InlineStructures {
  hyperlinks?: SlotHyperlink[];
  tabs?: SlotTab[];
  line_breaks_count?: number;
}

export interface SlotBudgets {
  max_lines?: number;
  max_chars?: number;
  hard_max_chars?: number;
  line_width_pt?: number;
  last_line_fill_ratio?: number;
}

export interface TextSlot {
  slot_id: string;
  section_id: string;
  item_id: string;
  bullet_id?: string | null;
  item_block_id?: string | null;
  role: TextSlotRole;
  binds?: string[];
  max_chars: number;
  max_lines: number;
  font: string;
  size: number;
  color?: string | null;
  source_pointer: SourcePointer;
  run_structure?: RunStructure;
  inline_structures?: InlineStructures;
  budgets?: SlotBudgets;
  confidence?: number;
  classification_source?: 'rule' | 'llm' | 'user_override';
  is_clonable?: boolean;
  prototype_xml_path?: string | null;
  literal_prefix?: string | null;
}

export interface SlotMapTarget {
  section_id: string;
  item_id: string;
  bullet_id?: string | null;
  target_field: string;
}

export type SlotMap = Record<string, SlotMapTarget>;

export interface ItemBlock {
  item_block_id: string;
  section_id: string;
  item_id: string;
  title_slot_id: string;
  meta_slot_id?: string | null;
  bullet_slot_ids: string[];
}

export interface FontReportEntry {
  original_name: string;
  in_container: boolean;
  substitute_used?: string | null;
  confidence: number;
}

export interface FidelityMetrics {
  page_count_match?: boolean;
  mean_line_delta_pt?: number;
  max_line_delta_pt?: number;
  run_property_match_rate?: number;
  ssim_score?: number;
}

export type TemplateStatus = 'ready' | 'warning' | 'failed';

export interface TemplateProfile {
  schema_version: SchemaVersion;
  template_profile_id: string;
  resume_id: string;
  version: number;
  source_type: TemplateSourceType;
  page_count: number;
  slots: TextSlot[];
  slot_map: SlotMap;
  item_blocks?: ItemBlock[];
  font_report?: FontReportEntry[];
  fidelity_score: number;
  fidelity_metrics?: FidelityMetrics;
  status: TemplateStatus;
  warnings?: string[];
}

/**
 * Generated from contracts/schemas/tailored_content.schema.json
 * Version 1.1.0 (with 1.0.0 backward compatibility)
 */

export type SchemaVersion = '1.0.0' | '1.1.0';

export type AllowedInlineMarkup = 'bold' | 'italic' | 'link';

export interface MarkupSyntaxGuide {
  bold: string;
  italic: string;
  link: string;
}

export interface TailoringRules {
  no_new_facts_allowed: true;
  allowed_inline_markup: AllowedInlineMarkup[];
  syntax_guide: MarkupSyntaxGuide;
}

export type ChangeType =
  | 'rewrite_bullet'
  | 'reorder_bullets'
  | 'reorder_items'
  | 'show_item'
  | 'hide_item'
  | 'reorder_skills'
  | 'regroup_skills'
  | 'rewrite_summary'
  | 'normalize_term'
  | 'add_item_from_master_profile';

export type RiskLevel = 'low' | 'medium' | 'high';
export type ChangeStatus = 'proposed' | 'accepted' | 'rejected' | 'auto_rejected';

export interface GeneratorMetadata {
  model: string;
  prompt_version: string;
  weights_version: string;
  taxonomy_version: string;
}

export interface SourceReference {
  source_item_id: string;
  source_bullet_id?: string;
  verified_fact: string;
  is_grounded: boolean;
}

export interface TailoredChange {
  change_id: string;
  type: ChangeType;
  target_content_id?: string;
  slot_id?: string;
  item_id?: string;
  field: string;
  before?: string | string[] | null;
  after?: string | string[] | null;
  reason: string;
  evidence_ids?: string[];
  keywords_touched?: string[];
  risk_level?: RiskLevel;
  status: ChangeStatus;
  rejection_reason?: string | null;
  generator?: GeneratorMetadata;

  // 1.0.0 backward-compatibility fields
  target_id?: string;
  original_text?: string;
  tailored_text?: string;
  source_reference?: SourceReference;
}

export interface ScoreBreakdown {
  required_skill_coverage: number;
  preferred_skill_coverage: number;
  semantic_relevance: number;
  seniority_fit: number;
  ats_readability: number;
  stuffing_penalty: number;
  confidence_note?: string | null;
}

export interface MatchedSkill {
  skill: string;
  canonical_name: string;
  category: string;
  content_ids: string[];
}

export interface MissingSkill {
  skill: string;
  canonical_name: string;
  category: string;
  importance: 'required' | 'preferred';
}

export interface PresentNotVisibleSkill {
  skill: string;
  canonical_name: string;
  master_item_id: string;
}

export interface AdjacentSkill {
  jd_skill: string;
  resume_skill: string;
  relation: string;
}

export interface SkillsAnalysis {
  matched_skills: MatchedSkill[];
  missing_skills: MissingSkill[];
  present_not_visible: PresentNotVisibleSkill[];
  adjacent_skills: AdjacentSkill[];
}

export interface Suggestion {
  suggestion_id: string;
  skill: string;
  canonical_name: string;
  category: string;
  class: 'missing' | 'present_not_visible' | 'adjacent';
  prompt_text: string;
  target_section_id?: string | null;
  confirmed: boolean;
}

export interface TailoredContent {
  schema_version: SchemaVersion;
  run_id: string;
  resume_id: string;
  job_description_id?: string | null;
  mode?: 'analyze' | 'full';
  rules: TailoringRules;
  score_before: number;
  score_after: number;
  score_breakdown?: ScoreBreakdown;
  skills_analysis?: SkillsAnalysis;
  generator?: GeneratorMetadata;
  changes: TailoredChange[];
  rejected_changes?: TailoredChange[];
  suggestions?: Suggestion[];
  matched_keywords: string[];
  missing_keywords: string[];
}

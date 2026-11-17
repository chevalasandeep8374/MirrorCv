/**
 * Generated from contracts/schemas/resume_content.schema.json (v1.1.0)
 * Single source of truth for resume content structure.
 */

export type SchemaVersion = '1.0.0' | '1.1.0';

export interface FieldVisibility {
  name?: boolean;
  title?: boolean;
  email?: boolean;
  phone?: boolean;
  location?: boolean;
  website?: boolean;
  photo?: boolean;
}

export interface ContactLink {
  id: string;
  label: string;
  url: string;
}

export interface HeaderContent {
  name: string;
  title: string;
  email: string;
  phone: string;
  location: string;
  website: string;
  photoUrl?: string | null;
  fieldVisibility?: FieldVisibility;
  links: ContactLink[];
}

export type SectionType =
  | 'summary'
  | 'experience'
  | 'skills'
  | 'education'
  | 'projects'
  | 'certifications'
  | 'custom'
  | 'languages'
  | 'awards'
  | 'publications'
  | 'volunteering'
  | 'interests'
  | 'references'
  | 'links';

export type ItemType = 'timeline' | 'list' | 'paragraph' | 'tags';

export interface StructuredDates {
  startMonth?: number | null;
  startYear?: number | null;
  endMonth?: number | null;
  endYear?: number | null;
  isCurrent?: boolean;
}

export interface ItemLink {
  label?: string;
  url?: string;
}

export interface BulletItem {
  id: string;
  text: string;
  level?: number;
  /** User-set proficiency rating 1-5. Agent 2 and verifier must never touch it. */
  proficiency?: number | null;
}

export interface SectionItem {
  id: string;
  title: string;
  subtitle: string;
  location: string;
  dateRange: string;
  /** Optional identifier grouping multiple promotional roles or related entries under one organization */
  groupId?: string | null;
  /** Structured date representation. When present, dateRange is synchronized and the renderer prefers dates. */
  dates?: StructuredDates | null;
  link?: ItemLink | null;
  visible?: boolean;
  itemType?: ItemType;
  bullets: BulletItem[];
}

export interface ResumeSection {
  id: string;
  type: SectionType;
  title: string;
  visible: boolean;
  pageBreakBefore?: boolean;
  order?: number;
  items: SectionItem[];
}

export interface RecipientContent {
  name?: string;
  title?: string;
  company?: string;
  address?: string;
  email?: string;
}

export interface CoverLetterParagraph {
  id: string;
  text: string;
}

export interface CoverLetterContent {
  sender: HeaderContent;
  recipient: RecipientContent;
  date: string;
  salutation: string;
  paragraphs: CoverLetterParagraph[];
  closing: string;
  signature: string;
}

export interface ResumeContent {
  schema_version?: SchemaVersion;
  header: HeaderContent;
  sections: ResumeSection[];
  coverLetter?: CoverLetterContent | null;
}

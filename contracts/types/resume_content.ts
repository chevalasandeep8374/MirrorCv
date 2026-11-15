/**
 * Generated from contracts/schemas/resume_content.schema.json
 */

export type SchemaVersion = '1.0.0';

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
  photoUrl?: string;
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

export interface BulletItem {
  id: string;
  text: string;
  level?: number;
}

export interface SectionItem {
  id: string;
  title: string;
  subtitle: string;
  location: string;
  dateRange: string;
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
  schema_version: SchemaVersion;
  header: HeaderContent;
  sections: ResumeSection[];
  coverLetter?: CoverLetterContent | null;
}

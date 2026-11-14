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
  links: ContactLink[];
}

export interface BulletItem {
  id: string;
  text: string;
}

export interface SectionItem {
  id: string;
  title: string;
  subtitle: string;
  location: string;
  dateRange: string;
  bullets: BulletItem[];
}

export type SectionType =
  | 'summary'
  | 'experience'
  | 'skills'
  | 'education'
  | 'projects'
  | 'certifications'
  | 'custom';

export interface ResumeSection {
  id: string;
  type: SectionType;
  title: string;
  visible: boolean;
  items: SectionItem[];
}

export interface ResumeContent {
  header: HeaderContent;
  sections: ResumeSection[];
}

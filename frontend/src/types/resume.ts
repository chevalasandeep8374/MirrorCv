import { ResumeContent } from './content';
import { ResumeStyle } from './style';

export interface Resume {
  id: string;
  userId: string;
  user_id?: string;
  title: string;
  content: ResumeContent;
  style: ResumeStyle;
  templateId?: string;
  template_id?: string;
  version: number;
  sourceType?: 'editor' | 'uploaded_docx' | 'uploaded_pdf';
  source_type?: 'editor' | 'uploaded_docx' | 'uploaded_pdf';
  isArchived?: boolean;
  is_archived?: boolean;
  tags?: string[];
  folder?: string | null;
  targetJobTitle?: string | null;
  target_job_title?: string | null;
  createdAt: string;
  created_at?: string;
  updatedAt: string;
  updated_at?: string;
}

export interface ResumeSummary {
  id: string;
  userId?: string;
  user_id?: string;
  title: string;
  docType?: string;
  doc_type?: string;
  targetJobTitle?: string | null;
  target_job_title?: string | null;
  tags: string[];
  folder?: string | null;
  isArchived?: boolean;
  is_archived?: boolean;
  version?: number;
  templateId?: string;
  template_id?: string;
  tailoredFromId?: string | null;
  tailored_from_id?: string | null;
  tailoredFromTitle?: string | null;
  tailored_from_title?: string | null;
  thumbnailPath?: string | null;
  thumbnail_path?: string | null;
  createdAt?: string;
  created_at?: string;
  updatedAt?: string;
  updated_at?: string;
}

export interface ResumeUpdatePayload {
  title?: string;
  content?: ResumeContent;
  style?: ResumeStyle;
  templateId?: string;
  template_id?: string;
  expected_version?: number;
  isArchived?: boolean;
  is_archived?: boolean;
  tags?: string[];
  folder?: string | null;
  targetJobTitle?: string | null;
  target_job_title?: string | null;
}

export interface User {
  id: string;
  email: string;
  fullName?: string;
  createdAt: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

import { ResumeContent } from './content';
import { ResumeStyle } from './style';

export interface Resume {
  id: string;
  userId: string;
  title: string;
  content: ResumeContent;
  style: ResumeStyle;
  createdAt: string;
  updatedAt: string;
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

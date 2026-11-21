import { ResumeStyle } from '@/types/style';
import { ResumeContent } from '@/types/content';

export const classicSingleColumnPreset: ResumeStyle = {
  templateId: 'classic-single-column',
  pageSize: 'A4',
  margins: { top: 36, bottom: 36, left: 42, right: 42, unit: 'pt' },
  typography: {
    baseFontFamily: 'Inter',
    headingFontFamily: 'Inter',
    nameFontFamily: 'Inter',
    fontSizeScale: 1.0,
    fontSizes: {
      name: 22,
      headerTitle: 11,
      contact: 9,
      sectionHeading: 12.5,
      itemTitle: 10.5,
      itemSubtitle: 9.5,
      body: 9.5,
      meta: 8.5,
      unit: 'pt',
    },
    lineHeight: 1.45,
  },
  spacing: {
    sectionSpacing: 14,
    itemSpacing: 8,
    bulletSpacing: 3,
    headerBottomSpacing: 16,
    unit: 'pt',
  },
  colors: {
    accent: '#4F46E5', // Modern Tech Indigo
    text: '#0F172A',
    muted: '#64748B',
    background: '#ffffff',
    sidebarBackground: '#f8fafc',
    divider: '#e2e8f0',
  },
  bulletStyle: 'disc',
  headingStyle: 'bar',
  layout: {
    type: 'single',
    sidebarWidthPercent: 32,
    sidebarSectionIds: [],
    mainSectionIds: [
      'sec-summary',
      'sec-exp',
      'sec-skills',
      'sec-proj',
      'sec-edu',
      'sec-cert',
    ],
  },
};

export const modernSidebarLeftPreset: ResumeStyle = {
  templateId: 'modern-sidebar-left',
  pageSize: 'A4',
  margins: { top: 32, bottom: 32, left: 32, right: 32, unit: 'pt' },
  typography: {
    baseFontFamily: 'Inter',
    headingFontFamily: 'Inter',
    fontSizeScale: 1.0,
    fontSizes: {
      name: 20,
      headerTitle: 11,
      contact: 8.5,
      sectionHeading: 12,
      itemTitle: 10,
      itemSubtitle: 9,
      body: 9,
      meta: 8,
      unit: 'pt',
    },
    lineHeight: 1.4,
  },
  spacing: {
    sectionSpacing: 12,
    itemSpacing: 7,
    bulletSpacing: 2.5,
    headerBottomSpacing: 14,
    unit: 'pt',
  },
  colors: {
    accent: '#0f766e', // Deep Teal
    text: '#1f2937',
    muted: '#6b7280',
    background: '#ffffff',
    sidebarBackground: '#f0fdfa',
    divider: '#cbd5e1',
  },
  bulletStyle: 'square',
  headingStyle: 'underline',
  layout: {
    type: 'sidebar_left',
    sidebarWidthPercent: 33,
    sidebarSectionIds: ['sec-skills', 'sec-edu', 'sec-cert', 'sec-lang'],
    mainSectionIds: ['sec-summary', 'sec-exp', 'sec-proj'],
  },
};
export const modernTwoColumnPreset = modernSidebarLeftPreset;

export const executiveSidebarRightPreset: ResumeStyle = {
  templateId: 'executive-sidebar-right',
  pageSize: 'A4',
  margins: { top: 36, bottom: 36, left: 36, right: 36, unit: 'pt' },
  typography: {
    baseFontFamily: 'Inter',
    headingFontFamily: 'Inter',
    fontSizeScale: 1.0,
    fontSizes: {
      name: 22,
      headerTitle: 11.5,
      contact: 9,
      sectionHeading: 12.5,
      itemTitle: 10.5,
      itemSubtitle: 9.5,
      body: 9.5,
      meta: 8.5,
      unit: 'pt',
    },
    lineHeight: 1.42,
  },
  spacing: {
    sectionSpacing: 14,
    itemSpacing: 8,
    bulletSpacing: 3,
    headerBottomSpacing: 16,
    unit: 'pt',
  },
  colors: {
    accent: '#18181b', // Charcoal
    text: '#0f172a',
    muted: '#64748b',
    background: '#ffffff',
    sidebarBackground: '#f8fafc',
    divider: '#e2e8f0',
  },
  bulletStyle: 'disc',
  headingStyle: 'bar',
  layout: {
    type: 'sidebar_right',
    sidebarWidthPercent: 34,
    sidebarSectionIds: ['sec-skills', 'sec-edu', 'sec-cert', 'sec-awards'],
    mainSectionIds: ['sec-summary', 'sec-exp', 'sec-proj'],
  },
};

export const headerBannerPreset: ResumeStyle = {
  templateId: 'header-banner',
  pageSize: 'A4',
  margins: { top: 28, bottom: 32, left: 36, right: 36, unit: 'pt' },
  typography: {
    baseFontFamily: 'Inter',
    headingFontFamily: 'Inter',
    fontSizeScale: 1.0,
    fontSizes: {
      name: 24,
      headerTitle: 12,
      contact: 9,
      sectionHeading: 12.5,
      itemTitle: 10.5,
      itemSubtitle: 9.5,
      body: 9.5,
      meta: 8.5,
      unit: 'pt',
    },
    lineHeight: 1.45,
  },
  spacing: {
    sectionSpacing: 13,
    itemSpacing: 7.5,
    bulletSpacing: 2.5,
    headerBottomSpacing: 18,
    unit: 'pt',
  },
  colors: {
    accent: '#3b82f6', // Bright Blue
    text: '#1e293b',
    muted: '#64748b',
    background: '#ffffff',
    sidebarBackground: '#f8fafc',
    divider: '#e2e8f0',
    headerBannerColor: '#0f172a',
    headerBannerTextColor: '#ffffff',
  },
  bulletStyle: 'circle',
  headingStyle: 'pill',
  layout: {
    type: 'header_banner',
    sidebarWidthPercent: 32,
    sidebarSectionIds: [],
    mainSectionIds: [
      'sec-summary',
      'sec-exp',
      'sec-skills',
      'sec-proj',
      'sec-edu',
      'sec-cert',
    ],
  },
  decorations: {
    headerBanner: true,
    headerBannerColor: '#0f172a',
    headerBannerTextColor: '#ffffff',
  },
};

export const compactDensePreset: ResumeStyle = {
  templateId: 'compact-dense',
  pageSize: 'A4',
  margins: { top: 24, bottom: 24, left: 28, right: 28, unit: 'pt' },
  typography: {
    baseFontFamily: 'Inter',
    headingFontFamily: 'Inter',
    fontSizeScale: 0.92,
    fontSizes: {
      name: 18,
      headerTitle: 10,
      contact: 8,
      sectionHeading: 11,
      itemTitle: 9.5,
      itemSubtitle: 8.5,
      body: 8.5,
      meta: 7.5,
      unit: 'pt',
    },
    lineHeight: 1.28,
  },
  spacing: {
    sectionSpacing: 9,
    itemSpacing: 5,
    bulletSpacing: 1.5,
    headerBottomSpacing: 10,
    unit: 'pt',
  },
  colors: {
    accent: '#2563eb',
    text: '#0f172a',
    muted: '#475569',
    background: '#ffffff',
    sidebarBackground: '#f8fafc',
    divider: '#cbd5e1',
  },
  bulletStyle: 'disc',
  headingStyle: 'plain',
  layout: {
    type: 'compact',
    sidebarWidthPercent: 30,
    sidebarSectionIds: [],
    mainSectionIds: [
      'sec-summary',
      'sec-exp',
      'sec-skills',
      'sec-proj',
      'sec-edu',
      'sec-cert',
    ],
  },
};

export const creativeAccentPreset: ResumeStyle = {
  templateId: 'creative-accent',
  pageSize: 'A4',
  margins: { top: 32, bottom: 32, left: 34, right: 34, unit: 'pt' },
  typography: {
    baseFontFamily: 'Inter',
    headingFontFamily: 'Inter',
    fontSizeScale: 1.0,
    fontSizes: {
      name: 22,
      headerTitle: 11.5,
      contact: 8.5,
      sectionHeading: 12,
      itemTitle: 10.5,
      itemSubtitle: 9,
      body: 9,
      meta: 8,
      unit: 'pt',
    },
    lineHeight: 1.42,
  },
  spacing: {
    sectionSpacing: 13,
    itemSpacing: 7.5,
    bulletSpacing: 2.5,
    headerBottomSpacing: 15,
    unit: 'pt',
  },
  colors: {
    accent: '#059669', // Emerald Green
    text: '#111827',
    muted: '#4b5563',
    background: '#ffffff',
    sidebarBackground: '#ecfdf5',
    divider: '#a7f3d0',
  },
  bulletStyle: 'arrow',
  headingStyle: 'boxed',
  layout: {
    type: 'creative',
    sidebarWidthPercent: 32,
    sidebarSectionIds: ['sec-skills', 'sec-edu', 'sec-cert'],
    mainSectionIds: ['sec-summary', 'sec-exp', 'sec-proj'],
  },
};

export const minimalEditorialPreset: ResumeStyle = {
  templateId: 'minimal-editorial',
  pageSize: 'A4',
  margins: { top: 40, bottom: 40, left: 44, right: 44, unit: 'pt' },
  typography: {
    baseFontFamily: 'Inter',
    headingFontFamily: 'Inter',
    fontSizeScale: 1.0,
    fontSizes: {
      name: 22,
      headerTitle: 11,
      contact: 8.5,
      sectionHeading: 12,
      itemTitle: 10,
      itemSubtitle: 9,
      body: 9,
      meta: 8,
      unit: 'pt',
    },
    lineHeight: 1.52,
  },
  spacing: {
    sectionSpacing: 16,
    itemSpacing: 9,
    bulletSpacing: 3.5,
    headerBottomSpacing: 18,
    unit: 'pt',
  },
  colors: {
    accent: '#09090b', // Pitch Black
    text: '#18181b',
    muted: '#71717a',
    background: '#ffffff',
    sidebarBackground: '#ffffff',
    divider: '#e4e4e7',
  },
  bulletStyle: 'dash',
  headingStyle: 'caps',
  layout: {
    type: 'minimal',
    sidebarWidthPercent: 30,
    sidebarSectionIds: [],
    mainSectionIds: [
      'sec-summary',
      'sec-exp',
      'sec-skills',
      'sec-proj',
      'sec-edu',
      'sec-cert',
    ],
  },
};

export const academicCvPreset: ResumeStyle = {
  templateId: 'academic-cv',
  pageSize: 'A4',
  margins: { top: 42, bottom: 42, left: 46, right: 46, unit: 'pt' },
  typography: {
    baseFontFamily: 'Liberation Serif',
    headingFontFamily: 'Liberation Serif',
    nameFontFamily: 'Liberation Serif',
    fontSizeScale: 1.02,
    fontSizes: {
      name: 24,
      headerTitle: 12,
      contact: 9.5,
      sectionHeading: 13,
      itemTitle: 11,
      itemSubtitle: 10,
      body: 10,
      meta: 9,
      unit: 'pt',
    },
    lineHeight: 1.48,
  },
  spacing: {
    sectionSpacing: 15,
    itemSpacing: 8.5,
    bulletSpacing: 3,
    headerBottomSpacing: 16,
    unit: 'pt',
  },
  colors: {
    accent: '#1e3a8a', // Classic Navy
    text: '#0f172a',
    muted: '#475569',
    background: '#ffffff',
    sidebarBackground: '#f8fafc',
    divider: '#cbd5e1',
  },
  bulletStyle: 'disc',
  headingStyle: 'underline',
  layout: {
    type: 'academic',
    sidebarWidthPercent: 30,
    sidebarSectionIds: [],
    mainSectionIds: [
      'sec-summary',
      'sec-edu',
      'sec-exp',
      'sec-proj',
      'sec-skills',
      'sec-cert',
    ],
  },
};

export interface TemplatePresetInfo {
  id: string;
  name: string;
  category: 'single' | 'sidebar' | 'banner' | 'compact' | 'creative' | 'minimal' | 'academic';
  description: string;
  style: ResumeStyle;
}

export const TEMPLATE_PRESETS: TemplatePresetInfo[] = [
  {
    id: 'classic-single-column',
    name: 'Classic Single Column',
    category: 'single',
    description: 'Timeless single-column design with clean bar headings and balanced margins.',
    style: classicSingleColumnPreset,
  },
  {
    id: 'modern-sidebar-left',
    name: 'Modern Left Sidebar',
    category: 'sidebar',
    description: 'Two-column layout with a shaded sidebar for skills, contact, and credentials.',
    style: modernSidebarLeftPreset,
  },
  {
    id: 'executive-sidebar-right',
    name: 'Executive Right Sidebar',
    category: 'sidebar',
    description: 'High-contrast right sidebar for certifications and education; primary space for experience.',
    style: executiveSidebarRightPreset,
  },
  {
    id: 'header-banner',
    name: 'Header Banner',
    category: 'banner',
    description: 'Prominent colored header card with crisp inverted white title typography.',
    style: headerBannerPreset,
  },
  {
    id: 'compact-dense',
    name: 'Compact Technical',
    category: 'compact',
    description: 'High-density formatting engineered to maximize content on a single page.',
    style: compactDensePreset,
  },
  {
    id: 'creative-accent',
    name: 'Creative Accent',
    category: 'creative',
    description: 'Vibrant emerald green accents, boxed section headings, and dynamic list arrows.',
    style: creativeAccentPreset,
  },
  {
    id: 'minimal-editorial',
    name: 'Minimal Editorial',
    category: 'minimal',
    description: 'Monochromatic typography-focused design with generous leading and hairline rules.',
    style: minimalEditorialPreset,
  },
  {
    id: 'academic-cv',
    name: 'Academic CV',
    category: 'academic',
    description: 'Formal serif curriculum vitae format with hanging indents for extensive credentials.',
    style: academicCvPreset,
  },
];

export const defaultResumeContent: ResumeContent = {
  header: {
    name: 'Alex Mercer',
    title: 'Senior Staff Software Engineer',
    email: 'alex.mercer@example.com',
    phone: '+1 (555) 019-2834',
    location: 'San Francisco, CA',
    website: 'https://alexmercer.dev',
    links: [
      { id: 'link-1', label: 'GitHub', url: 'https://github.com/alexmercer' },
      { id: 'link-2', label: 'LinkedIn', url: 'https://linkedin.com/in/alexmercer' },
    ],
  },
  sections: [
    {
      id: 'sec-summary',
      type: 'summary',
      title: 'Professional Summary',
      visible: true,
      items: [
        {
          id: 'item-sum-1',
          title: '',
          subtitle: '',
          location: '',
          dateRange: '',
          bullets: [
            {
              id: 'b-sum-1',
              text: 'Accomplished full-stack systems engineer with 9+ years building high-throughput web applications, cloud infrastructure, and document layout engines. Proven track record leading distributed engineering teams and delivering 99.99% reliability across critical SaaS products.',
            },
          ],
        },
      ],
    },
    {
      id: 'sec-exp',
      type: 'experience',
      title: 'Work Experience',
      visible: true,
      items: [
        {
          id: 'item-exp-1',
          title: 'Principal Software Engineer',
          subtitle: 'Acme Cloud Platforms',
          location: 'San Francisco, CA',
          dateRange: '2021 - Present',
          bullets: [
            {
              id: 'b-exp-1',
              text: 'Architected high-concurrency document rendering microservices processing 4.2M daily export jobs with sub-500ms latency.',
            },
            {
              id: 'b-exp-2',
              text: 'Reduced AWS infrastructure costs by 38% ($450K ARR) via intelligent container right-sizing and spot fleet orchestration in EKS.',
            },
            {
              id: 'b-exp-3',
              text: 'Established engineering excellence standards, RFC technical review processes, and mentored 14 engineers.',
            },
          ],
        },
        {
          id: 'item-exp-2',
          title: 'Senior Full-Stack Engineer',
          subtitle: 'Nexus Global Technologies',
          location: 'New York, NY',
          dateRange: '2018 - 2021',
          bullets: [
            {
              id: 'b-exp-4',
              text: 'Led front-end migration of flagship analytics dashboard from Angular to Next.js and TypeScript, improving Core Web Vitals score from 54 to 98.',
            },
            {
              id: 'b-exp-5',
              text: 'Designed and rolled out real-time collaborative editing features utilizing WebSockets and CRDTs.',
            },
          ],
        },
        {
          id: 'item-exp-3',
          title: 'Software Engineer',
          subtitle: 'Velocity Labs',
          location: 'Boston, MA',
          dateRange: '2016 - 2018',
          bullets: [
            {
              id: 'b-exp-6',
              text: 'Implemented RESTful and GraphQL APIs in Python/FastAPI with PostgreSQL and Redis caching.',
            },
            {
              id: 'b-exp-7',
              text: 'Developed comprehensive unit and integration test suites achieving 94% code coverage.',
            },
          ],
        },
      ],
    },
    {
      id: 'sec-skills',
      type: 'skills',
      title: 'Technical Skills',
      visible: true,
      items: [
        {
          id: 'item-sk-1',
          title: 'Frontend',
          subtitle: '',
          location: '',
          dateRange: '',
          bullets: [
            {
              id: 'b-sk-1',
              text: 'TypeScript, React, Next.js, Tailwind CSS, Playwright, Web Audio/Canvas, Redux/Zustand',
            },
          ],
        },
        {
          id: 'item-sk-2',
          title: 'Backend & Cloud',
          subtitle: '',
          location: '',
          dateRange: '',
          bullets: [
            {
              id: 'b-sk-2',
              text: 'Python, FastAPI, SQLAlchemy, PostgreSQL, Redis, Docker, Kubernetes, AWS (ECS, RDS)',
            },
          ],
        },
        {
          id: 'item-sk-3',
          title: 'Architecture & Practices',
          subtitle: '',
          location: '',
          dateRange: '',
          bullets: [
            {
              id: 'b-sk-3',
              text: 'Microservices, Distributed Systems, Event-Driven Architecture, CI/CD, OpenTelemetry',
            },
          ],
        },
      ],
    },
    {
      id: 'sec-proj',
      type: 'projects',
      title: 'Key Projects',
      visible: true,
      items: [
        {
          id: 'item-pr-1',
          title: 'DocMorph Engine',
          subtitle: 'Headless Style Token Extraction',
          location: '',
          dateRange: '2023 - 2024',
          bullets: [
            {
              id: 'b-pr-1',
              text: 'Created open-source layout parser extracting typography, margins, and palette tokens from PDF/DOCX binaries with 98% fidelity.',
            },
            {
              id: 'b-pr-2',
              text: 'Over 1,800 GitHub stars and 12,000 monthly PyPI downloads.',
            },
          ],
        },
      ],
    },
    {
      id: 'sec-edu',
      type: 'education',
      title: 'Education',
      visible: true,
      items: [
        {
          id: 'item-edu-1',
          title: 'B.S. in Computer Science',
          subtitle: 'University of California, Berkeley',
          location: 'Berkeley, CA',
          dateRange: '2012 - 2016',
          bullets: [
            {
              id: 'b-edu-1',
              text: 'Graduated Magna Cum Laude; President of ACM Student Chapter.',
            },
          ],
        },
      ],
    },
    {
      id: 'sec-cert',
      type: 'certifications',
      title: 'Certifications',
      visible: true,
      items: [
        {
          id: 'item-cert-1',
          title: 'AWS Solutions Architect – Professional',
          subtitle: 'Amazon Web Services',
          location: '',
          dateRange: '2023',
          bullets: [],
        },
        {
          id: 'item-cert-2',
          title: 'Certified Kubernetes Administrator (CKA)',
          subtitle: 'Linux Foundation',
          location: '',
          dateRange: '2022',
          bullets: [],
        },
      ],
    },
  ],
};

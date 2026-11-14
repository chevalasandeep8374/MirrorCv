import { ResumeStyle } from '@/types/style';
import { ResumeContent } from '@/types/content';

export const classicSingleColumnPreset: ResumeStyle = {
  templateId: 'classic-single-column',
  pageSize: 'A4',
  margins: {
    top: 36,
    bottom: 36,
    left: 42,
    right: 42,
    unit: 'pt',
  },
  typography: {
    baseFontFamily: 'Inter',
    headingFontFamily: 'Inter',
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
    accent: '#2563eb', // Royal Blue
    text: '#111827',
    muted: '#4b5563',
    background: '#ffffff',
    sidebarBackground: '#f8fafc',
    divider: '#e5e7eb',
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

export const modernTwoColumnPreset: ResumeStyle = {
  templateId: 'modern-two-column',
  pageSize: 'A4',
  margins: {
    top: 32,
    bottom: 32,
    left: 32,
    right: 32,
    unit: 'pt',
  },
  typography: {
    baseFontFamily: 'Inter',
    headingFontFamily: 'Inter',
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
    accent: '#0f766e', // Teal
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
    sidebarSectionIds: ['sec-skills', 'sec-edu', 'sec-cert'],
    mainSectionIds: ['sec-summary', 'sec-exp', 'sec-proj'],
  },
};

export const TEMPLATE_PRESETS: { id: string; name: string; description: string; style: ResumeStyle }[] = [
  {
    id: 'classic-single-column',
    name: 'Classic Single-Column',
    description: 'Traditional chronological layout with bold section bars and royal blue accents.',
    style: classicSingleColumnPreset,
  },
  {
    id: 'modern-two-column',
    name: 'Modern Two-Column Sidebar',
    description: 'Contemporary dual-column format with skills & education highlighted in a soft sidebar.',
    style: modernTwoColumnPreset,
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

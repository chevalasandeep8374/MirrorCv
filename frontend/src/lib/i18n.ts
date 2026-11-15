import { SectionType } from '@/types/content';

export type SupportedLocale = 'en' | 'hi' | 'ar' | 'he' | 'fr' | 'es' | 'de';

export interface LocaleInfo {
  code: SupportedLocale;
  name: string;
  nativeName: string;
  direction: 'ltr' | 'rtl';
  fontFallback: string;
}

export const SUPPORTED_LOCALES: Record<SupportedLocale, LocaleInfo> = {
  en: {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    direction: 'ltr',
    fontFallback: "'Inter', 'Roboto', 'Liberation Sans', sans-serif",
  },
  hi: {
    code: 'hi',
    name: 'Hindi',
    nativeName: 'हिन्दी',
    direction: 'ltr',
    fontFallback: "'Noto Sans Devanagari', 'Noto Serif Devanagari', sans-serif",
  },
  ar: {
    code: 'ar',
    name: 'Arabic',
    nativeName: 'العربية',
    direction: 'rtl',
    fontFallback: "'Noto Sans Arabic', 'Cairo', sans-serif",
  },
  he: {
    code: 'he',
    name: 'Hebrew',
    nativeName: 'עברית',
    direction: 'rtl',
    fontFallback: "'Noto Sans Hebrew', 'Arial', sans-serif",
  },
  fr: {
    code: 'fr',
    name: 'French',
    nativeName: 'Français',
    direction: 'ltr',
    fontFallback: "'Inter', 'Roboto', 'Liberation Sans', sans-serif",
  },
  es: {
    code: 'es',
    name: 'Spanish',
    nativeName: 'Español',
    direction: 'ltr',
    fontFallback: "'Inter', 'Roboto', 'Liberation Sans', sans-serif",
  },
  de: {
    code: 'de',
    name: 'German',
    nativeName: 'Deutsch',
    direction: 'ltr',
    fontFallback: "'Inter', 'Roboto', 'Liberation Sans', sans-serif",
  },
};

export const SECTION_TRANSLATIONS: Record<SupportedLocale, Record<SectionType, string>> = {
  en: {
    summary: 'Professional Summary',
    experience: 'Work Experience',
    education: 'Education',
    skills: 'Skills',
    projects: 'Projects',
    certifications: 'Certifications',
    languages: 'Languages',
    awards: 'Awards & Honors',
    publications: 'Publications',
    volunteering: 'Volunteering',
    interests: 'Interests',
    references: 'References',
    links: 'Links',
    custom: 'Custom Section',
  },
  hi: {
    summary: 'व्यावसायिक सारांश',
    experience: 'कार्य अनुभव',
    education: 'शिक्षा',
    skills: 'कौशल',
    projects: 'परियोजनाएं',
    certifications: 'प्रमाणपत्र',
    languages: 'भाषाएं',
    awards: 'पुरस्कार एवं सम्मान',
    publications: 'प्रकाशन',
    volunteering: 'स्वयंसेवा',
    interests: 'रुचियां',
    references: 'संदर्भ',
    links: 'वेब लिंक',
    custom: 'अनुकूलित अनुभाग',
  },
  ar: {
    summary: 'الملخص المهني',
    experience: 'الخبرة المهنية',
    education: 'التعليم والشهادات',
    skills: 'المهارات والتقنيات',
    projects: 'المشاريع',
    certifications: 'الشهادات المهنية',
    languages: 'اللغات',
    awards: 'الجوائز والتكريم',
    publications: 'المنشورات',
    volunteering: 'العمل التطوعي',
    interests: 'الاهتمامات',
    references: 'المراجع',
    links: 'الروابط',
    custom: 'قسم مخصص',
  },
  he: {
    summary: 'תקציר מקצועי',
    experience: 'ניסיון תעסוקתי',
    education: 'השכלה',
    skills: 'כישורים ויכולות',
    projects: 'פרויקטים',
    certifications: 'הסמכות ותעודות',
    languages: 'שפות',
    awards: 'פרסים והוקרה',
    publications: 'פרסומים',
    volunteering: 'התנדבות',
    interests: 'תחומי עניין',
    references: 'המלצות',
    links: 'קישורים',
    custom: 'חלק מותאם אישית',
  },
  fr: {
    summary: 'Résumé Professionnel',
    experience: 'Expérience Professionnelle',
    education: 'Formation',
    skills: 'Compétences',
    projects: 'Projets',
    certifications: 'Certifications',
    languages: 'Langues',
    awards: 'Prix et Distinctions',
    publications: 'Publications',
    volunteering: 'Bénévolat',
    interests: "Centres d'intérêt",
    references: 'Références',
    links: 'Liens',
    custom: 'Section Personnalisée',
  },
  es: {
    summary: 'Resumen Profesional',
    experience: 'Experiencia Laboral',
    education: 'Educación',
    skills: 'Habilidades',
    projects: 'Proyectos',
    certifications: 'Certificaciones',
    languages: 'Idiomas',
    awards: 'Premios y Honores',
    publications: 'Publicaciones',
    volunteering: 'Voluntariado',
    interests: 'Intereses',
    references: 'Referencias',
    links: 'Enlaces',
    custom: 'Sección Personalizada',
  },
  de: {
    summary: 'Beruflicher Werdegang',
    experience: 'Berufserfahrung',
    education: 'Ausbildung',
    skills: 'Kenntnisse',
    projects: 'Projekte',
    certifications: 'Zertifikate',
    languages: 'Sprachen',
    awards: 'Auszeichnungen',
    publications: 'Publikationen',
    volunteering: 'Ehrenamt',
    interests: 'Interessen',
    references: 'Referenzen',
    links: 'Links',
    custom: 'Eigener Bereich',
  },
};

export function isRtlLocale(locale?: string): boolean {
  if (!locale) return false;
  return locale === 'ar' || locale === 'he';
}

export function getLocaleDirection(locale?: string): 'ltr' | 'rtl' {
  return isRtlLocale(locale) ? 'rtl' : 'ltr';
}

export function getFontFallbackForLocale(locale?: string): string {
  const loc = (locale || 'en') as SupportedLocale;
  return SUPPORTED_LOCALES[loc]?.fontFallback || SUPPORTED_LOCALES.en.fontFallback;
}

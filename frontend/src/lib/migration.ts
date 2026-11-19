import { ResumeContent, StructuredDates } from '@/types/content';
import { ResumeStyle, FontSizeOffsets } from '@/types/style';

const MONTH_NAMES = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
];

/**
 * Format structured dates into a standardized string representation based on dateFormat.
 */
export function formatStructuredDate(
  dates?: StructuredDates | null,
  dateFormat: string = 'MMM YYYY'
): string {
  if (!dates) return '';

  const formatPart = (month?: number | null, year?: number | null): string => {
    if (!year) return '';
    if (dateFormat === 'YYYY') return String(year);
    if (month && month >= 1 && month <= 12) {
      if (dateFormat === 'MM/YYYY') {
        return `${String(month).padStart(2, '0')}/${year}`;
      }
      return `${MONTH_NAMES[month - 1]} ${year}`;
    }
    return String(year);
  };

  const startStr = formatPart(dates.startMonth, dates.startYear);
  const endStr = dates.isCurrent ? 'Present' : formatPart(dates.endMonth, dates.endYear);

  if (startStr && endStr) return `${startStr} – ${endStr}`;
  if (startStr) return startStr;
  if (endStr) return endStr;
  return '';
}

/**
 * Deterministic pure function to normalize ResumeContent and ResumeStyle to 1.1.0 specifications.
 * Guarantees 100% backward compatibility for legacy 1.0.0 rows.
 */
export function normalizeResumeTokens(
  rawContent: ResumeContent,
  rawStyle: ResumeStyle
): { content: ResumeContent; style: ResumeStyle } {
  // Deep clone to ensure pure transformation
  const content: ResumeContent = JSON.parse(JSON.stringify(rawContent));
  const style: ResumeStyle = JSON.parse(JSON.stringify(rawStyle));

  // 1. Content normalization
  content.schema_version = '1.1.0';

  if (!content.header) {
    content.header = {
      name: '',
      title: '',
      email: '',
      phone: '',
      location: '',
      website: '',
      links: [],
    };
  }

  content.header.fieldVisibility = {
    name: true,
    title: true,
    email: true,
    phone: true,
    location: true,
    website: true,
    photo: true,
    ...(content.header.fieldVisibility || {}),
  };

  if (Array.isArray(content.sections)) {
    content.sections.forEach((section) => {
      section.visible = section.visible !== false;
      if (Array.isArray(section.items)) {
        section.items.forEach((item) => {
          item.visible = item.visible !== false;
          item.itemType = item.itemType || 'timeline';
          item.groupId = item.groupId ?? null;

          // Date synchronization rule: when structured dates exist, dateRange is updated
          if (item.dates && (item.dates.startYear || item.dates.isCurrent)) {
            item.dateRange = formatStructuredDate(item.dates, style.dateFormat || 'MMM YYYY');
          }

          if (Array.isArray(item.bullets)) {
            item.bullets.forEach((b) => {
              b.level = b.level ?? 0;
              b.proficiency = b.proficiency ?? null;
            });
          }
        });
      }
    });
  }

  // 2. Style normalization
  style.schema_version = '1.1.0';
  style.isLocked =
    style.isLocked ??
    (typeof style.templateId === 'string' && style.templateId.startsWith('uploaded:'));

  // Normalize lengths to pt
  if (style.margins) {
    style.margins.unit = 'pt';
  }
  if (style.spacing) {
    style.spacing.unit = 'pt';
  }

  // Typography font size model migration (Base size + relative offsets)
  const legacyFontSizes = style.typography?.fontSizes;
  const scale = style.typography?.fontSizeScale ?? 1.0;

  if (!style.typography.fontSizeOffsets && legacyFontSizes) {
    const baseFontSize = Number(((legacyFontSizes.body || 9.5) * scale).toFixed(2));
    style.typography.baseFontSize = baseFontSize;

    const roundOffset = (val?: number) =>
      Number((((val || baseFontSize) * scale) - baseFontSize).toFixed(2));

    style.typography.fontSizeOffsets = {
      name: roundOffset(legacyFontSizes.name),
      headerTitle: roundOffset(legacyFontSizes.headerTitle),
      contact: roundOffset(legacyFontSizes.contact),
      sectionHeading: roundOffset(legacyFontSizes.sectionHeading),
      itemTitle: roundOffset(legacyFontSizes.itemTitle),
      itemSubtitle: roundOffset(legacyFontSizes.itemSubtitle),
      body: 0.0,
      meta: roundOffset(legacyFontSizes.meta),
    };
  } else if (!style.typography.fontSizeOffsets) {
    style.typography.baseFontSize = style.typography.baseFontSize || 9.5;
    style.typography.fontSizeOffsets = {
      name: 12.5,
      headerTitle: 1.5,
      contact: -0.5,
      sectionHeading: 3.0,
      itemTitle: 1.0,
      itemSubtitle: 0.0,
      body: 0.0,
      meta: -1.0,
    };
  } else {
    style.typography.baseFontSize = style.typography.baseFontSize || 9.5;
  }
  style.typography.fontSizeScale = 1.0; // Ambiguity eliminated

  // Colors & Accent toggles
  if (!style.colors) {
    style.colors = {
      accent: '#2563eb',
      text: '#111827',
      muted: '#4b5563',
      background: '#ffffff',
      sidebarBackground: '#f8fafc',
      divider: '#e5e7eb',
    };
  }
  style.colors.area = style.colors.area || 'full_page';
  style.colors.mode = style.colors.mode || 'single';
  style.colors.backgroundOverlayOpacity = style.colors.backgroundOverlayOpacity ?? 0.6;
  style.colors.accentToggles = {
    name: false,
    jobTitle: false,
    headings: true,
    headingsLine: true,
    headerIcons: true,
    bullets: true,
    dates: false,
    entryTitle: false,
    entrySubtitle: false,
    linkIcons: true,
    ...(style.colors.accentToggles || {}),
  };

  // Entry Layout
  style.entryLayout = {
    structure: 'full_width',
    dateLocationPosition: 'right',
    headerSplitRatio: 'auto',
    ...(style.entryLayout || {}),
  };

  // Heading Config
  style.heading = {
    capitalization: 'none',
    iconStyle: 'none',
    ...(style.heading || {}),
  };

  // Header Config
  style.header = {
    alignment: 'left',
    arrangement: 'bullet',
    ...(style.header || {}),
  };

  // Photo Config
  style.photo = {
    shape: 'circle',
    size: 'medium',
    border: 'none',
    position: 'right',
    ...(style.photo || {}),
  };

  // Link Styling
  style.linkStyling = {
    underline: true,
    colored: false,
    showIcon: true,
    ...(style.linkStyling || {}),
  };

  // Footer Config
  style.footer = {
    showPageNumbers: true,
    showEmail: false,
    showName: false,
    ...(style.footer || {}),
  };

  // Layout Placement
  if (style.layout) {
    style.layout.sectionPlacement = style.layout.sectionPlacement || {};
  }

  // Section Customizations
  style.sectionCustomizations = {
    summary: { inHeader: false, showHeading: true, ...(style.sectionCustomizations?.summary || {}) },
    skills: {
      style: 'rows',
      rowSpacing: 'tight',
      startRowsWithBullets: false,
      subInfoStyle: 'colon',
      ...(style.sectionCustomizations?.skills || {}),
    },
    experience: {
      titleSubtitleOrder: 'title_first',
      groupPromotions: true,
      ...(style.sectionCustomizations?.experience || {}),
    },
    education: {
      titleSubtitleOrder: 'title_first',
      ...(style.sectionCustomizations?.education || {}),
    },
    certificates: {
      style: 'compact',
      ...(style.sectionCustomizations?.certificates || {}),
    },
    languages: {
      style: 'chips',
      ...(style.sectionCustomizations?.languages || {}),
    },
    interests: {
      style: 'chips',
      ...(style.sectionCustomizations?.interests || {}),
    },
    declaration: {
      showPlace: true,
      showDate: true,
      ...(style.sectionCustomizations?.declaration || {}),
    },
  };

  return { content, style };
}

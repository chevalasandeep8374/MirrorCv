import { CSSProperties } from 'react';
import { ResumeStyle } from '@/types/style';
import { getFontFallbackForLocale } from '@/lib/i18n';

export function getStyleCssVariables(style: ResumeStyle): CSSProperties {
  const { typography, spacing, margins, colors, layout, decorations, locale } = style;
  const fUnit = typography.fontSizes?.unit || 'pt';
  const sUnit = spacing.unit || 'pt';
  const mUnit = margins.unit || 'pt';
  const scale = typography.fontSizeScale ?? 1.0;
  const fallback = getFontFallbackForLocale(locale);

  // Unified Font Size Model (Base size + relative offsets)
  let fontSizeName: number;
  let fontSizeHeaderTitle: number;
  let fontSizeContact: number;
  let fontSizeSectionHeading: number;
  let fontSizeItemTitle: number;
  let fontSizeItemSubtitle: number;
  let fontSizeBody: number;
  let fontSizeMeta: number;

  if (typography.fontSizeOffsets) {
    const base = typography.baseFontSize ?? 9.5;
    const offsets = typography.fontSizeOffsets;
    fontSizeName = base + (offsets.name ?? 12.5);
    fontSizeHeaderTitle = base + (offsets.headerTitle ?? 1.5);
    fontSizeContact = base + (offsets.contact ?? -0.5);
    fontSizeSectionHeading = base + (offsets.sectionHeading ?? 3.0);
    fontSizeItemTitle = base + (offsets.itemTitle ?? 1.0);
    fontSizeItemSubtitle = base + (offsets.itemSubtitle ?? 0.0);
    fontSizeBody = base + (offsets.body ?? 0.0);
    fontSizeMeta = base + (offsets.meta ?? -1.0);
  } else if (typography.fontSizes) {
    fontSizeName = (typography.fontSizes.name ?? 22) * scale;
    fontSizeHeaderTitle = (typography.fontSizes.headerTitle ?? 12) * scale;
    fontSizeContact = (typography.fontSizes.contact ?? 9) * scale;
    fontSizeSectionHeading = (typography.fontSizes.sectionHeading ?? 12) * scale;
    fontSizeItemTitle = (typography.fontSizes.itemTitle ?? 10) * scale;
    fontSizeItemSubtitle = (typography.fontSizes.itemSubtitle ?? 9) * scale;
    fontSizeBody = (typography.fontSizes.body ?? 9.5) * scale;
    fontSizeMeta = (typography.fontSizes.meta ?? 8.5) * scale;
  } else {
    const base = typography.baseFontSize ?? 9.5;
    fontSizeName = base + 12.5;
    fontSizeHeaderTitle = base + 1.5;
    fontSizeContact = base - 0.5;
    fontSizeSectionHeading = base + 3.0;
    fontSizeItemTitle = base + 1.0;
    fontSizeItemSubtitle = base;
    fontSizeBody = base;
    fontSizeMeta = base - 1.0;
  }

  const accents = colors.accentToggles;

  return {
    // Fonts
    '--font-base': `${typography.baseFontFamily}, ${fallback}`,
    '--font-heading': `${typography.headingFontFamily}, ${fallback}`,
    '--font-name': `${typography.nameFontFamily || typography.headingFontFamily}, ${fallback}`,
    '--line-height': typography.lineHeight.toString(),

    // Font Sizes
    '--font-size-name': `${fontSizeName.toFixed(1)}${fUnit}`,
    '--font-size-header-title': `${fontSizeHeaderTitle.toFixed(1)}${fUnit}`,
    '--font-size-contact': `${fontSizeContact.toFixed(1)}${fUnit}`,
    '--font-size-section-heading': `${fontSizeSectionHeading.toFixed(1)}${fUnit}`,
    '--font-size-item-title': `${fontSizeItemTitle.toFixed(1)}${fUnit}`,
    '--font-size-item-subtitle': `${fontSizeItemSubtitle.toFixed(1)}${fUnit}`,
    '--font-size-body': `${fontSizeBody.toFixed(1)}${fUnit}`,
    '--font-size-meta': `${fontSizeMeta.toFixed(1)}${fUnit}`,

    // Spacing
    '--spacing-section': `${spacing.sectionSpacing}${sUnit}`,
    '--spacing-item': `${spacing.itemSpacing}${sUnit}`,
    '--spacing-bullet': `${spacing.bulletSpacing}${sUnit}`,
    '--spacing-header-bottom': `${spacing.headerBottomSpacing}${sUnit}`,

    // Margins
    '--margin-top': `${margins.top}${mUnit}`,
    '--margin-bottom': `${margins.bottom}${mUnit}`,
    '--margin-left': `${margins.left}${mUnit}`,
    '--margin-right': `${margins.right}${mUnit}`,

    // Colors
    '--color-accent': colors.accent,
    '--color-text': colors.text,
    '--color-muted': colors.muted,
    '--color-background': colors.background,
    '--color-sidebar-background': colors.sidebarBackground,
    '--color-divider': colors.divider,
    '--color-header-banner': colors.headerBannerColor || decorations?.headerBannerColor || '#0f172a',
    '--color-header-banner-text': colors.headerBannerTextColor || decorations?.headerBannerTextColor || '#ffffff',

    // Granular Accent Toggles
    '--accent-name': accents?.name ? colors.accent : 'inherit',
    '--accent-job-title': accents?.jobTitle ? colors.accent : 'inherit',
    '--accent-headings': accents?.headings !== false ? colors.accent : 'inherit',
    '--accent-headings-line': accents?.headingsLine !== false ? colors.accent : 'var(--color-divider)',
    '--accent-bullets': accents?.bullets !== false ? colors.accent : 'var(--color-text)',
    '--accent-dates': accents?.dates ? colors.accent : 'var(--color-muted)',
    '--accent-entry-title': accents?.entryTitle ? colors.accent : 'inherit',
    '--accent-entry-subtitle': accents?.entrySubtitle ? colors.accent : 'inherit',
    '--accent-link-icons': accents?.linkIcons !== false ? colors.accent : 'var(--color-muted)',

    // Layout
    '--sidebar-width': `${layout.sidebarWidthPercent}%`,
  } as CSSProperties;
}

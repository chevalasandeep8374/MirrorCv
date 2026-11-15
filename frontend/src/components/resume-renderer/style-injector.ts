import { CSSProperties } from 'react';
import { ResumeStyle } from '@/types/style';
import { getFontFallbackForLocale } from '@/lib/i18n';

export function getStyleCssVariables(style: ResumeStyle): CSSProperties {
  const { typography, spacing, margins, colors, layout, decorations, locale } = style;
  const fUnit = typography.fontSizes.unit;
  const sUnit = spacing.unit;
  const mUnit = margins.unit;
  const scale = typography.fontSizeScale ?? 1.0;
  const fallback = getFontFallbackForLocale(locale);

  return {
    // Fonts
    '--font-base': `${typography.baseFontFamily}, ${fallback}`,
    '--font-heading': `${typography.headingFontFamily}, ${fallback}`,
    '--font-name': `${typography.nameFontFamily || typography.headingFontFamily}, ${fallback}`,
    '--line-height': typography.lineHeight.toString(),

    // Font Sizes (scaled)
    '--font-size-name': `${(typography.fontSizes.name * scale).toFixed(1)}${fUnit}`,
    '--font-size-header-title': `${(typography.fontSizes.headerTitle * scale).toFixed(1)}${fUnit}`,
    '--font-size-contact': `${(typography.fontSizes.contact * scale).toFixed(1)}${fUnit}`,
    '--font-size-section-heading': `${(typography.fontSizes.sectionHeading * scale).toFixed(1)}${fUnit}`,
    '--font-size-item-title': `${(typography.fontSizes.itemTitle * scale).toFixed(1)}${fUnit}`,
    '--font-size-item-subtitle': `${(typography.fontSizes.itemSubtitle * scale).toFixed(1)}${fUnit}`,
    '--font-size-body': `${(typography.fontSizes.body * scale).toFixed(1)}${fUnit}`,
    '--font-size-meta': `${(typography.fontSizes.meta * scale).toFixed(1)}${fUnit}`,

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

    // Layout
    '--sidebar-width': `${layout.sidebarWidthPercent}%`,
  } as CSSProperties;
}

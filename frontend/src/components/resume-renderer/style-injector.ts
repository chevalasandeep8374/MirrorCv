import { CSSProperties } from 'react';
import { ResumeStyle } from '@/types/style';

export function getStyleCssVariables(style: ResumeStyle): CSSProperties {
  const { typography, spacing, margins, colors, layout } = style;
  const fUnit = typography.fontSizes.unit;
  const sUnit = spacing.unit;
  const mUnit = margins.unit;

  return {
    // Fonts
    '--font-base': `${typography.baseFontFamily}, system-ui, -apple-system, sans-serif`,
    '--font-heading': `${typography.headingFontFamily}, system-ui, -apple-system, sans-serif`,
    '--line-height': typography.lineHeight.toString(),

    // Font Sizes
    '--font-size-name': `${typography.fontSizes.name}${fUnit}`,
    '--font-size-header-title': `${typography.fontSizes.headerTitle}${fUnit}`,
    '--font-size-contact': `${typography.fontSizes.contact}${fUnit}`,
    '--font-size-section-heading': `${typography.fontSizes.sectionHeading}${fUnit}`,
    '--font-size-item-title': `${typography.fontSizes.itemTitle}${fUnit}`,
    '--font-size-item-subtitle': `${typography.fontSizes.itemSubtitle}${fUnit}`,
    '--font-size-body': `${typography.fontSizes.body}${fUnit}`,
    '--font-size-meta': `${typography.fontSizes.meta}${fUnit}`,

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

    // Layout
    '--sidebar-width': `${layout.sidebarWidthPercent}%`,
  } as CSSProperties;
}

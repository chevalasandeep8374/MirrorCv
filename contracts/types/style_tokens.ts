/**
 * Generated from contracts/schemas/style_tokens.schema.json
 */

export type SchemaVersion = '1.0.0';
export type PageSize = 'A4' | 'Letter';
export type Unit = 'pt' | 'px';
export type BulletStyle = 'disc' | 'circle' | 'square' | 'dash' | 'arrow' | 'none';
export type HeadingStyle = 'underline' | 'bar' | 'plain' | 'caps' | 'boxed' | 'pill';
export type ColumnLayoutType =
  | 'single'
  | 'sidebar_left'
  | 'sidebar_right'
  | 'header_banner'
  | 'compact'
  | 'creative'
  | 'minimal'
  | 'academic';

export interface Margins {
  top: number;
  bottom: number;
  left: number;
  right: number;
  unit: Unit;
}

export interface FontSizes {
  name: number;
  headerTitle: number;
  contact: number;
  sectionHeading: number;
  itemTitle: number;
  itemSubtitle: number;
  body: number;
  meta: number;
  unit: Unit;
}

export interface Typography {
  baseFontFamily: string;
  headingFontFamily: string;
  nameFontFamily?: string;
  fontSizeScale?: number;
  fontSizes: FontSizes;
  lineHeight: number;
}

export interface Spacing {
  sectionSpacing: number;
  itemSpacing: number;
  bulletSpacing: number;
  headerBottomSpacing: number;
  unit: Unit;
}

export interface Colors {
  accent: string;
  text: string;
  muted: string;
  background: string;
  sidebarBackground: string;
  divider: string;
  headerBannerColor?: string;
  headerBannerTextColor?: string;
}

export interface ColumnLayout {
  type: ColumnLayoutType;
  sidebarWidthPercent: number;
  sidebarSectionIds: string[];
  mainSectionIds: string[];
}

export interface Decorations {
  headerBanner?: boolean;
  headerBannerColor?: string;
  headerBannerTextColor?: string;
  avatarShape?: 'circle' | 'square';
  showAvatar?: boolean;
  avatarUrl?: string;
}

export interface StyleTokens {
  schema_version: SchemaVersion;
  templateId: string;
  pageSize: PageSize;
  margins: Margins;
  typography: Typography;
  spacing: Spacing;
  colors: Colors;
  bulletStyle: BulletStyle;
  headingStyle: HeadingStyle;
  layout: ColumnLayout;
  decorations?: Decorations;
  dateFormat?: string;
  locale?: 'en' | 'hi' | 'ar' | 'he' | 'fr' | 'es' | 'de';
  direction?: 'ltr' | 'rtl';
}

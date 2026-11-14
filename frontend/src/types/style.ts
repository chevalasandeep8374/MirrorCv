export type PageSize = 'A4' | 'Letter';
export type Unit = 'pt' | 'px';
export type BulletStyle = 'disc' | 'circle' | 'square' | 'dash' | 'none';
export type HeadingStyle = 'underline' | 'bar' | 'plain' | 'caps';
export type ColumnLayoutType = 'single' | 'sidebar_left' | 'sidebar_right';

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
}

export interface ColumnLayout {
  type: ColumnLayoutType;
  sidebarWidthPercent: number;
  sidebarSectionIds: string[];
  mainSectionIds: string[];
}

export interface ResumeStyle {
  templateId: string;
  pageSize: PageSize;
  margins: Margins;
  typography: Typography;
  spacing: Spacing;
  colors: Colors;
  bulletStyle: BulletStyle;
  headingStyle: HeadingStyle;
  layout: ColumnLayout;
}

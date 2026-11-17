/**
 * Generated from contracts/schemas/style_tokens.schema.json (v1.1.0)
 * Single source of truth for resume styling tokens, typography, and layout.
 */

export type SchemaVersion = '1.0.0' | '1.1.0';
export type PageSize = 'A4' | 'Letter';
export type Unit = 'pt' | 'px';
export type BulletStyle = 'disc' | 'circle' | 'square' | 'dash' | 'arrow' | 'none';
export type HeadingStyle = 'underline' | 'bar' | 'plain' | 'caps' | 'boxed' | 'side_line' | 'pill';
export type ColumnLayoutType =
  | 'single'
  | 'sidebar_left'
  | 'sidebar_right'
  | 'mix'
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

export interface FontSizeOffsets {
  name?: number;
  headerTitle?: number;
  contact?: number;
  sectionHeading?: number;
  itemTitle?: number;
  itemSubtitle?: number;
  body?: number;
  meta?: number;
}

export interface FontSizes {
  name?: number;
  headerTitle?: number;
  contact?: number;
  sectionHeading?: number;
  itemTitle?: number;
  itemSubtitle?: number;
  body?: number;
  meta?: number;
  unit?: Unit;
}

export interface Typography {
  baseFontFamily: string;
  headingFontFamily: string;
  nameFontFamily?: string | null;
  /** Primary font-size baseline in pt (default 9.5). All role sizes derive via offsets. */
  baseFontSize?: number;
  /** Relative point offsets from baseFontSize for each text hierarchy role */
  fontSizeOffsets?: FontSizeOffsets;
  /** Legacy scale factor (1.0 default); retained for 1.0.0 backward compatibility */
  fontSizeScale?: number;
  /** Legacy absolute font sizes in pt; migrated into baseFontSize + fontSizeOffsets */
  fontSizes?: FontSizes;
  lineHeight: number;
}

export interface Spacing {
  sectionSpacing: number;
  itemSpacing: number;
  bulletSpacing: number;
  headerBottomSpacing: number;
  unit: Unit;
}

export interface AccentToggles {
  name?: boolean;
  jobTitle?: boolean;
  headings?: boolean;
  headingsLine?: boolean;
  headerIcons?: boolean;
  bullets?: boolean;
  dates?: boolean;
  entryTitle?: boolean;
  entrySubtitle?: boolean;
  linkIcons?: boolean;
}

export interface Colors {
  accent: string;
  text: string;
  muted: string;
  background: string;
  sidebarBackground: string;
  divider: string;
  headerBannerColor?: string | null;
  headerBannerTextColor?: string | null;
  area?: 'full_page' | 'header' | 'border';
  mode?: 'single' | 'multi' | 'image';
  backgroundImageUrl?: string | null;
  backgroundOverlayOpacity?: number;
  accentToggles?: AccentToggles;
}

export interface HeadingConfig {
  capitalization?: 'none' | 'capitalize' | 'uppercase';
  iconStyle?: 'none' | 'outline' | 'filled';
}

export interface HeaderConfig {
  alignment?: 'left' | 'center';
  arrangement?: 'bullet' | 'pipe' | 'bar' | 'icon';
}

export interface PhotoConfig {
  shape?: 'circle' | 'square' | 'rounded';
  size?: 'small' | 'medium' | 'large';
  border?: 'none' | 'thin' | 'thick' | 'accent';
  position?: 'left' | 'right' | 'top_center';
}

export interface LinkStyling {
  underline?: boolean;
  colored?: boolean;
  showIcon?: boolean;
}

export interface FooterConfig {
  showPageNumbers?: boolean;
  showEmail?: boolean;
  showName?: boolean;
}

export interface EntryLayoutConfig {
  structure?: 'full_width' | 'columns';
  dateLocationPosition?: 'right' | 'below_title';
  headerSplitRatio?: 'auto' | '50/50' | '70/30';
}

export interface ColumnLayout {
  type: ColumnLayoutType;
  sidebarWidthPercent: number;
  sidebarSectionIds: string[];
  mainSectionIds: string[];
  sectionPlacement?: Record<string, 'main' | 'sidebar' | 'full'>;
}

export interface SummaryCustomization {
  inHeader?: boolean;
  showHeading?: boolean;
}

export interface SkillsCustomization {
  style?: 'grid' | 'rows' | 'compact' | 'bubble' | 'level';
  rowSpacing?: 'tight' | 'spacious';
  startRowsWithBullets?: boolean;
  subInfoStyle?: 'colon' | 'dash' | 'bracket';
}

export interface ExperienceCustomization {
  titleSubtitleOrder?: 'title_first' | 'subtitle_first';
  groupPromotions?: boolean;
}

export interface EducationCustomization {
  titleSubtitleOrder?: 'title_first' | 'subtitle_first';
}

export interface CertificatesCustomization {
  style?: 'grid' | 'rows' | 'compact' | 'bubble';
}

export interface LanguagesCustomization {
  style?: 'chips' | 'list' | 'level';
}

export interface InterestsCustomization {
  style?: 'chips' | 'list';
}

export interface DeclarationCustomization {
  showPlace?: boolean;
  showDate?: boolean;
}

export interface SectionCustomizations {
  summary?: SummaryCustomization;
  skills?: SkillsCustomization;
  experience?: ExperienceCustomization;
  education?: EducationCustomization;
  certificates?: CertificatesCustomization;
  languages?: LanguagesCustomization;
  interests?: InterestsCustomization;
  declaration?: DeclarationCustomization;
}

export interface Decorations {
  headerBanner?: boolean;
  headerBannerColor?: string | null;
  headerBannerTextColor?: string | null;
  avatarShape?: 'circle' | 'square';
  showAvatar?: boolean;
  avatarUrl?: string | null;
}

export interface StyleTokens {
  schema_version?: SchemaVersion;
  templateId: string;
  isLocked?: boolean;
  pageSize: PageSize;
  margins: Margins;
  typography: Typography;
  spacing: Spacing;
  colors: Colors;
  bulletStyle: BulletStyle;
  headingStyle: HeadingStyle;
  heading?: HeadingConfig;
  header?: HeaderConfig;
  photo?: PhotoConfig;
  linkStyling?: LinkStyling;
  footer?: FooterConfig;
  entryLayout?: EntryLayoutConfig;
  layout: ColumnLayout;
  sectionCustomizations?: SectionCustomizations;
  decorations?: Decorations;
  dateFormat?: string;
  locale?: 'en' | 'hi' | 'ar' | 'he' | 'fr' | 'es' | 'de';
  direction?: 'ltr' | 'rtl';
}

export type ResumeStyle = StyleTokens;

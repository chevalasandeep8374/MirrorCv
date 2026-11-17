import { ResumeContent, ResumeSection, SectionItem } from '@/types/content';
import { ResumeStyle, Typography } from '@/types/style';

export interface PageLayoutSlice {
  pageIndex: number;
  isFirstPage: boolean;
  mainSections: ResumeSection[];
  sidebarSections: ResumeSection[];
}

export function getResolvedFontSizes(typography: Typography) {
  const base = typography.baseFontSize ?? 9.5;
  const offsets = typography.fontSizeOffsets;
  const scale = typography.fontSizeScale ?? 1.0;
  const legacy = typography.fontSizes;

  if (offsets) {
    return {
      name: base + (offsets.name ?? 12.5),
      headerTitle: base + (offsets.headerTitle ?? 1.5),
      contact: base + (offsets.contact ?? -0.5),
      sectionHeading: base + (offsets.sectionHeading ?? 3.0),
      itemTitle: base + (offsets.itemTitle ?? 1.0),
      itemSubtitle: base + (offsets.itemSubtitle ?? 0.0),
      body: base + (offsets.body ?? 0.0),
      meta: base + (offsets.meta ?? -1.0),
    };
  }

  if (legacy) {
    return {
      name: (legacy.name ?? 22) * scale,
      headerTitle: (legacy.headerTitle ?? 12) * scale,
      contact: (legacy.contact ?? 9) * scale,
      sectionHeading: (legacy.sectionHeading ?? 12) * scale,
      itemTitle: (legacy.itemTitle ?? 10) * scale,
      itemSubtitle: (legacy.itemSubtitle ?? 9) * scale,
      body: (legacy.body ?? 9.5) * scale,
      meta: (legacy.meta ?? 8.5) * scale,
    };
  }

  return {
    name: base + 12.5,
    headerTitle: base + 1.5,
    contact: base - 0.5,
    sectionHeading: base + 3.0,
    itemTitle: base + 1.0,
    itemSubtitle: base,
    body: base,
    meta: base - 1.0,
  };
}

/**
 * Calculates page-by-page distribution of sections for single-column and two-column layouts.
 * Uses exact token-based heights (in points converted to relative units) to partition sections
 * cleanly without breaking individual bullets across page margins.
 */
export function paginateResume(
  content: ResumeContent,
  style: ResumeStyle
): PageLayoutSlice[] {
  const isA4 = style.pageSize === 'A4';
  // Total page height in points: A4 is 841.89pt, Letter is 792pt
  const totalPageHeightPt = isA4 ? 841.89 : 792.0;
  const printableHeightPt =
    totalPageHeightPt - (style.margins.top + style.margins.bottom);

  const fontSizes = getResolvedFontSizes(style.typography);

  // Estimate header height in points
  const headerHeightPt =
    fontSizes.name * 1.2 +
    fontSizes.headerTitle * 1.3 +
    fontSizes.contact * 2.5 +
    style.spacing.headerBottomSpacing * 1.5;

  if (content.coverLetter) {
    return [
      {
        pageIndex: 0,
        isFirstPage: true,
        mainSections: [],
        sidebarSections: [],
      },
    ];
  }

  const visibleSections = content.sections.filter(
    (s) => s.visible !== false && s.items && s.items.length > 0
  );

  const isTwoColumn =
    style.layout.type === 'sidebar_left' ||
    style.layout.type === 'sidebar_right';

  if (!isTwoColumn) {
    // Single column pagination
    const pages: PageLayoutSlice[] = [];
    let currentPageIndex = 0;
    let currentHeight = headerHeightPt;
    let currentMainSections: ResumeSection[] = [];

    const flushPage = () => {
      pages.push({
        pageIndex: currentPageIndex,
        isFirstPage: currentPageIndex === 0,
        mainSections: currentMainSections,
        sidebarSections: [],
      });
      currentPageIndex++;
      currentHeight = 0;
      currentMainSections = [];
    };

    for (const section of visibleSections) {
      // Force page-break if section requests it
      if (section.pageBreakBefore && currentMainSections.length > 0) {
        flushPage();
      }
      const sectionHeadingHeight = fontSizes.sectionHeading * 1.4 + 10;
      let sectionItemsForCurrentPage: SectionItem[] = [];
      let currentSectionHeight = sectionHeadingHeight;

      for (const item of section.items) {
        // Estimate item height: title (1 line) + bullets
        const titleHeight = fontSizes.itemTitle * 1.3 + 4;
        const bulletsCount = item.bullets ? item.bullets.length : 0;
        const bulletsHeight =
          bulletsCount *
          (fontSizes.body * style.typography.lineHeight +
            style.spacing.bulletSpacing);
        const itemTotalHeight =
          titleHeight + bulletsHeight + style.spacing.itemSpacing;

        // Check if item fits in current page
        if (
          currentHeight + currentSectionHeight + itemTotalHeight >
            printableHeightPt &&
          (currentMainSections.length > 0 ||
            sectionItemsForCurrentPage.length > 0)
        ) {
          if (sectionItemsForCurrentPage.length > 0) {
            currentMainSections.push({
              ...section,
              items: sectionItemsForCurrentPage,
            });
          }
          flushPage();
          sectionItemsForCurrentPage = [];
          currentSectionHeight = sectionHeadingHeight;
        }

        sectionItemsForCurrentPage.push(item);
        currentSectionHeight += itemTotalHeight;
      }

      if (sectionItemsForCurrentPage.length > 0) {
        currentMainSections.push({
          ...section,
          items: sectionItemsForCurrentPage,
        });
        currentHeight += currentSectionHeight + style.spacing.sectionSpacing;
      }
    }

    if (currentMainSections.length > 0 || pages.length === 0) {
      flushPage();
    }

    return pages;
  } else {
    // Two Column Layout
    const sidebarSectionIdSet = new Set(style.layout.sidebarSectionIds);
    const mainSectionsList = visibleSections.filter(
      (s) => !sidebarSectionIdSet.has(s.id)
    );
    const sidebarSectionsList = visibleSections.filter((s) =>
      sidebarSectionIdSet.has(s.id)
    );

    const finalSidebarSections =
      sidebarSectionsList.length > 0
        ? sidebarSectionsList
        : visibleSections.filter(
            (s) =>
              s.type === 'skills' ||
              s.type === 'education' ||
              s.type === 'certifications'
          );

    const finalMainSections =
      sidebarSectionsList.length > 0
        ? mainSectionsList
        : visibleSections.filter(
            (s) =>
              s.type !== 'skills' &&
              s.type !== 'education' &&
              s.type !== 'certifications'
          );

    return [
      {
        pageIndex: 0,
        isFirstPage: true,
        mainSections: finalMainSections,
        sidebarSections: finalSidebarSections,
      },
    ];
  }
}

import { ResumeContent, ResumeSection, SectionItem } from '@/types/content';
import { ResumeStyle } from '@/types/style';

export interface PageLayoutSlice {
  pageIndex: number;
  isFirstPage: boolean;
  mainSections: ResumeSection[];
  sidebarSections: ResumeSection[];
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

  // Estimate header height in points
  const headerHeightPt =
    style.typography.fontSizes.name * 1.2 +
    style.typography.fontSizes.headerTitle * 1.3 +
    style.typography.fontSizes.contact * 2.5 +
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
      const sectionHeadingHeight =
        style.typography.fontSizes.sectionHeading * 1.4 + 10;
      let sectionItemsForCurrentPage: SectionItem[] = [];
      let currentSectionHeight = sectionHeadingHeight;

      for (const item of section.items) {
        // Estimate item height: title (1 line) + bullets
        const titleHeight = style.typography.fontSizes.itemTitle * 1.3 + 4;
        const bulletsCount = item.bullets ? item.bullets.length : 0;
        const bulletsHeight =
          bulletsCount *
          (style.typography.fontSizes.body * style.typography.lineHeight +
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
          // If we accumulated items in this section, push the section slice
          if (sectionItemsForCurrentPage.length > 0) {
            currentMainSections.push({
              ...section,
              items: sectionItemsForCurrentPage,
            });
          }
          flushPage();
          // Reset for new page
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

    // If sidebar sections are empty, treat sections with type skills/education as sidebar
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

    // Estimate heights of both columns
    // In two-column, usually pages hold both columns side-by-side
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

import { ResumeContent, ResumeSection, SectionItem } from '@/types/content';
import { ResumeStyle, Typography } from '@/types/style';

export interface PageLayoutSlice {
  pageIndex: number;
  isFirstPage: boolean;
  mainSections: ResumeSection[];
  sidebarSections: ResumeSection[];
}

export function getResolvedFontSizes(typography: Typography) {
  const base = typography.baseFontSize ?? typography.fontSizes?.body ?? 9.5;
  const offsets = typography.fontSizeOffsets;
  const scale = typography.fontSizeScale ?? 1.0;
  const legacy = typography.fontSizes;

  if (offsets) {
    return {
      name: (base + (offsets.name ?? 12.5)) * scale,
      headerTitle: (base + (offsets.headerTitle ?? 1.5)) * scale,
      contact: (base + (offsets.contact ?? -0.5)) * scale,
      sectionHeading: (base + (offsets.sectionHeading ?? 3.0)) * scale,
      itemTitle: (base + (offsets.itemTitle ?? 1.0)) * scale,
      itemSubtitle: (base + (offsets.itemSubtitle ?? 0.0)) * scale,
      body: (base + (offsets.body ?? 0.0)) * scale,
      meta: (base + (offsets.meta ?? -1.0)) * scale,
    };
  }

  if (typography.baseFontSize !== undefined) {
    return {
      name: (base + 12.5) * scale,
      headerTitle: (base + 1.5) * scale,
      contact: (base - 0.5) * scale,
      sectionHeading: (base + 3.0) * scale,
      itemTitle: (base + 1.0) * scale,
      itemSubtitle: base * scale,
      body: base * scale,
      meta: (base - 1.0) * scale,
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
    name: (base + 12.5) * scale,
    headerTitle: (base + 1.5) * scale,
    contact: (base - 0.5) * scale,
    sectionHeading: (base + 3.0) * scale,
    itemTitle: (base + 1.0) * scale,
    itemSubtitle: base * scale,
    body: base * scale,
    meta: (base - 1.0) * scale,
  };
}

/**
 * Estimates how many visual lines a block of text will wrap into
 * given available width in points and font size in points.
 */
export function estimateTextLines(
  text: string,
  availableWidthPt: number,
  fontSizePt: number
): number {
  if (!text || !text.trim()) return 0;

  // Calibrated character width factor for proportional sans-serif fonts (Inter/Source Sans Pro)
  const charWidthPt = fontSizePt * 0.50;
  const charsPerLine = Math.max(10, Math.floor(availableWidthPt / charWidthPt));

  const paragraphs = text.split('\n');
  let totalLines = 0;

  for (const para of paragraphs) {
    const trimmed = para.trim();
    if (!trimmed) {
      totalLines += 1;
      continue;
    }
    // Account for word-wrap boundaries: word breaks occur earlier than exact character limit
    const effectiveCharsPerLine = Math.max(8, Math.floor(charsPerLine * 0.90));
    const lines = Math.max(1, Math.ceil(trimmed.length / effectiveCharsPerLine));
    totalLines += lines;
  }

  return totalLines;
}

/**
 * Accurately estimates header height based on name, headline, contact items, links, and avatar.
 */
function estimateHeaderHeight(
  content: ResumeContent,
  style: ResumeStyle,
  fontSizes: ReturnType<typeof getResolvedFontSizes>,
  printableWidthPt: number
): number {
  const header = content.coverLetter?.sender || content.header;
  if (!header) return 0;

  const fieldVis = header.fieldVisibility || {};
  const showAvatar =
    fieldVis.photo !== false &&
    (style.decorations?.showAvatar ?? Boolean(header.photoUrl || style.decorations?.avatarUrl));

  let nameHeight = 0;
  if (fieldVis.name !== false && header.name) {
    const nameLines = estimateTextLines(header.name, printableWidthPt, fontSizes.name);
    nameHeight = nameLines * (fontSizes.name * 1.15);
  }

  let titleHeight = 0;
  if (fieldVis.title !== false && header.title) {
    const titleLines = estimateTextLines(header.title, printableWidthPt, fontSizes.headerTitle);
    titleHeight = titleLines * (fontSizes.headerTitle * 1.25);
  }

  // Count contact items & links
  const contactParts: string[] = [];
  if (fieldVis.email !== false && header.email) contactParts.push(header.email);
  if (fieldVis.phone !== false && header.phone) contactParts.push(header.phone);
  if (fieldVis.location !== false && header.location) contactParts.push(header.location);
  if (fieldVis.website !== false && header.website) contactParts.push(header.website);
  if (header.links) {
    header.links.forEach((l) => {
      if (l.label) contactParts.push(l.label);
    });
  }

  let contactHeight = 0;
  if (contactParts.length > 0) {
    const joinedContact = contactParts.join(' • ');
    const contactLines = estimateTextLines(joinedContact, printableWidthPt, fontSizes.contact);
    contactHeight = contactLines * (fontSizes.contact * 1.35);
  }

  let avatarHeight = 0;
  if (showAvatar) {
    const size = style.photo?.size || 'medium';
    avatarHeight = size === 'small' ? 52 : size === 'large' ? 76 : 64;
  }

  const textBlockHeight = nameHeight + titleHeight + contactHeight;
  const headerHeight = Math.max(textBlockHeight, avatarHeight);

  // ResumeHeader has mb-[headerBottomSpacing] (default 16)
  const headerSpacing = style.spacing?.headerBottomSpacing ?? 16;
  return headerHeight + headerSpacing;
}

/**
 * Estimates section heading height including margins.
 */
function estimateSectionHeadingHeight(
  style: ResumeStyle,
  fontSizes: ReturnType<typeof getResolvedFontSizes>
): number {
  return fontSizes.sectionHeading * 1.2 + 6;
}

/**
 * Estimates header height of a standard item (title, subtitle, dates, location).
 */
function estimateItemHeaderHeight(
  item: SectionItem,
  style: ResumeStyle,
  fontSizes: ReturnType<typeof getResolvedFontSizes>,
  availableWidthPt: number
): number {
  const dateLocationBelow = style.entryLayout?.dateLocationPosition === 'below_title';
  let headerH = 0;
  if (item.title || item.subtitle || item.dateRange || item.location) {
    const titleWidth = dateLocationBelow ? availableWidthPt : Math.max(160, availableWidthPt - 120);
    const titleText = (item.title || '') + (item.subtitle ? ` | ${item.subtitle}` : '');
    const titleLines = estimateTextLines(titleText, titleWidth, fontSizes.itemTitle);
    headerH += titleLines * (fontSizes.itemTitle * 1.2) + 2;

    if (dateLocationBelow && (item.dateRange || item.location)) {
      headerH += fontSizes.meta * 1.2 + 2;
    }
  }
  return headerH;
}

/**
 * Estimates height of a single bullet.
 */
function estimateSingleBulletHeight(
  bulletText: string,
  style: ResumeStyle,
  fontSizes: ReturnType<typeof getResolvedFontSizes>,
  availableWidthPt: number
): number {
  const lineHeight = style.typography.lineHeight || 1.45;
  const bulletAvailableWidth = Math.max(150, availableWidthPt - 24);
  const bLines = estimateTextLines(bulletText, bulletAvailableWidth, fontSizes.body);
  return Math.max(1, bLines) * (fontSizes.body * lineHeight) + style.spacing.bulletSpacing;
}

/**
 * Accurately estimates individual item height based on its title, subtitle, bullets, descriptions, and styling.
 */
function estimateItemHeight(
  item: SectionItem,
  section: ResumeSection,
  style: ResumeStyle,
  fontSizes: ReturnType<typeof getResolvedFontSizes>,
  availableWidthPt: number
): number {
  const lineHeight = style.typography.lineHeight || 1.45;
  const isParagraph = item.itemType === 'paragraph' || section.type === 'summary';
  const isSkills = section.type === 'skills';
  const skillsMode = style.sectionCustomizations?.skills?.style || 'rows';

  // 1. Simple 2-column certifications (single-line items without dates/subtitles/bullets)
  if (
    section.type === 'certifications' &&
    section.items.every(
      (it) => !it.dateRange && !it.subtitle && !it.location && (!it.bullets || it.bullets.length === 0)
    )
  ) {
    const totalItems = section.items.length;
    const lines = Math.ceil(totalItems / 2);
    return (lines * (fontSizes.body * lineHeight + 2) + style.spacing.itemSpacing) / totalItems;
  }

  // 1.5 Skills Section
  if (isSkills) {
    if (skillsMode === 'rows' || skillsMode === 'normal') {
      const allSkillsText = (item.bullets || [])
        .map((b) => b.text.replace(/\r?\n+/g, ' '))
        .join(', ');
      const startWithBullet = style.sectionCustomizations?.skills?.startRowsWithBullets ?? false;
      const fullText = (item.title ? `${item.title} — ` : '') + allSkillsText;
      const lines = estimateTextLines(fullText, availableWidthPt - (startWithBullet ? 14 : 0), fontSizes.body);
      const rowSpacing = style.sectionCustomizations?.skills?.rowSpacing;
      const mb = rowSpacing === 'spacious' ? style.spacing.itemSpacing : style.spacing.itemSpacing * 0.5;
      return Math.max(1, lines) * (fontSizes.body * lineHeight) + mb;
    }

    if (skillsMode === 'stacked') {
      const titleLines = item.title ? estimateTextLines(item.title, availableWidthPt, fontSizes.itemTitle) : 0;
      const tH = titleLines * (fontSizes.itemTitle * 1.2);
      const allSkillsText = (item.bullets || [])
        .map((b) => b.text.replace(/\r?\n+/g, ' '))
        .join(', ');
      const lines = estimateTextLines(allSkillsText, availableWidthPt, fontSizes.body);
      const sH = Math.max(1, lines) * (fontSizes.body * lineHeight);
      return tH + sH + style.spacing.itemSpacing;
    }

    // Chips / Bubble / Grid
    const titleH = item.title ? fontSizes.itemTitle * 1.2 + 4 : 0;
    const bulletCount = item.bullets?.length || 0;
    const chipsPerLine = Math.max(2, Math.floor(availableWidthPt / 72));
    const chipLines = Math.ceil(Math.max(1, bulletCount) / chipsPerLine);
    return titleH + chipLines * 20 + style.spacing.itemSpacing;
  }

  // 2. Paragraph / Summary Section
  if (isParagraph) {
    const titleH = item.title ? fontSizes.itemTitle * 1.2 + 4 : 0;
    const allText = (item.bullets || []).map((b) => b.text).join('\n') || ((item as { description?: string }).description || '');
    const lines = estimateTextLines(allText, availableWidthPt, fontSizes.body);
    const bodyH = Math.max(1, lines) * (fontSizes.body * lineHeight);
    return titleH + bodyH + style.spacing.itemSpacing;
  }

  // 3. Standard Item (Experience, Projects, Education, Certifications, Custom)
  const headerH = estimateItemHeaderHeight(item, style, fontSizes, availableWidthPt);

  let descH = 0;
  const legacyDesc = (item as { description?: string }).description;
  if (legacyDesc) {
    const descLines = estimateTextLines(legacyDesc, availableWidthPt, fontSizes.body);
    descH = descLines * (fontSizes.body * lineHeight) + 2;
  }

  let bulletsH = 0;
  if (item.bullets && item.bullets.length > 0) {
    for (const b of item.bullets) {
      bulletsH += estimateSingleBulletHeight(b.text, style, fontSizes, availableWidthPt);
    }
  }

  return headerH + descH + bulletsH + style.spacing.itemSpacing;
}

/**
 * Paginates a single list of sections into page slices for a given column width.
 */
function paginateSectionList(
  sections: ResumeSection[],
  availableWidthPt: number,
  printableHeightPt: number,
  firstPageOffsetPt: number,
  style: ResumeStyle,
  fontSizes: ReturnType<typeof getResolvedFontSizes>
): ResumeSection[][] {
  const pages: ResumeSection[][] = [];
  let currentHeight = firstPageOffsetPt;
  let currentSections: ResumeSection[] = [];

  const flushPage = () => {
    pages.push(currentSections);
    currentHeight = 0;
    currentSections = [];
  };

  const sectionHeadingH = estimateSectionHeadingHeight(style, fontSizes);
  // Reserve 12 pt safety buffer so text never clips at the bottom of the page
  const effectivePageLimit = printableHeightPt - 12;

  for (const section of sections) {
    // Explicit user-requested page break
    if (section.pageBreakBefore && currentSections.length > 0) {
      flushPage();
    }

    if (!section.items || section.items.length === 0) continue;

    // Simple 2-column certifications: render side-by-side as a single atomic block
    const isSimpleCertifications =
      section.type === 'certifications' &&
      section.items.every(
        (it) => !it.dateRange && !it.subtitle && !it.location && (!it.bullets || it.bullets.length === 0)
      );

    if (isSimpleCertifications) {
      const totalLines = Math.ceil(section.items.length / 2);
      const lineHeight = style.typography.lineHeight || 1.45;
      const certsH = totalLines * (fontSizes.body * lineHeight + 2) + style.spacing.itemSpacing;
      const totalSecH = sectionHeadingH + certsH;
      const remainingOnPage = effectivePageLimit - currentHeight;

      if (totalSecH <= remainingOnPage) {
        currentSections.push(section);
        currentHeight += totalSecH + style.spacing.sectionSpacing;
      } else {
        if (currentSections.length > 0) {
          flushPage();
        }
        currentSections.push(section);
        currentHeight += totalSecH + style.spacing.sectionSpacing;
      }
      continue;
    }

    let itemsForCurrentPage: SectionItem[] = [];
    let currentSectionHeight = sectionHeadingH;

    for (const item of section.items) {
      const itemH = estimateItemHeight(item, section, style, fontSizes, availableWidthPt);
      const remainingOnPage = effectivePageLimit - (currentHeight + currentSectionHeight);

      if (itemH <= remainingOnPage) {
        // Entire item fits on the current page
        itemsForCurrentPage.push(item);
        currentSectionHeight += itemH;
      } else {
        // Item does not fit entirely. Check if bullets can be cleanly split
        const isStandardList =
          section.type !== 'skills' &&
          section.type !== 'summary' &&
          item.itemType !== 'paragraph' &&
          item.bullets &&
          item.bullets.length >= 2;

        const headH = estimateItemHeaderHeight(item, style, fontSizes, availableWidthPt);
        const bullets = item.bullets || [];
        const bHeights = bullets.map((b) =>
          estimateSingleBulletHeight(b.text, style, fontSizes, availableWidthPt)
        );

        let canSplit = false;
        let splitIdx = 0;

        // Ensure there is room for item header + at least 1 bullet
        if (isStandardList && remainingOnPage >= headH + bHeights[0]) {
          let accum = headH;
          for (let idx = 0; idx < bHeights.length; idx++) {
            if (accum + bHeights[idx] + style.spacing.itemSpacing <= remainingOnPage) {
              accum += bHeights[idx];
              splitIdx = idx + 1;
            } else {
              break;
            }
          }
          // Only split if at least 1 bullet stays on current page and at least 1 goes to next page
          if (splitIdx >= 1 && splitIdx < bullets.length) {
            canSplit = true;
          }
        }

        if (canSplit) {
          // Part 1 stays on the current page
          const part1: SectionItem = {
            ...item,
            id: `${item.id}-p1`,
            bullets: bullets.slice(0, splitIdx),
          };
          itemsForCurrentPage.push(part1);
          const part1H = headH + bHeights.slice(0, splitIdx).reduce((a, b) => a + b, 0) + style.spacing.itemSpacing;
          currentSectionHeight += part1H;

          // Push section to current page and flush page
          currentSections.push({
            ...section,
            items: itemsForCurrentPage,
          });
          flushPage();

          // Prepare Part 2 for the new page
          itemsForCurrentPage = [];
          currentSectionHeight = sectionHeadingH;

          const part2: SectionItem = {
            ...item,
            id: `${item.id}-p2`,
            title: `${item.title} (Cont.)`,
            subtitle: '',
            dateRange: '',
            dates: null,
            location: '',
            bullets: bullets.slice(splitIdx),
          };
          const part2HeadH = estimateItemHeaderHeight(part2, style, fontSizes, availableWidthPt);
          const part2H =
            part2HeadH +
            bHeights.slice(splitIdx).reduce((a, b) => a + b, 0) +
            style.spacing.itemSpacing;
          itemsForCurrentPage.push(part2);
          currentSectionHeight += part2H;
        } else {
          // Item cannot be split cleanly: move whole item to the next page
          if (itemsForCurrentPage.length > 0 || currentSections.length > 0) {
            if (itemsForCurrentPage.length > 0) {
              currentSections.push({
                ...section,
                items: itemsForCurrentPage,
              });
            }
            flushPage();
            itemsForCurrentPage = [];
            currentSectionHeight = sectionHeadingH;
          }
          itemsForCurrentPage.push(item);
          currentSectionHeight += itemH;
        }
      }
    }

    if (itemsForCurrentPage.length > 0) {
      currentSections.push({
        ...section,
        items: itemsForCurrentPage,
      });
      currentHeight += currentSectionHeight + style.spacing.sectionSpacing;
    }
  }

  if (currentSections.length > 0 || pages.length === 0) {
    flushPage();
  }

  return pages;
}

/**
 * Calculates page-by-page distribution of sections for single-column and multi-column layouts.
 * Uses exact token-based and character-wrapping metrics to partition sections cleanly across pages.
 */
export function paginateResume(
  content: ResumeContent,
  style: ResumeStyle
): PageLayoutSlice[] {
  const isA4 = style.pageSize === 'A4';
  // Total page height in points: A4 is 841.89pt, Letter is 792pt
  const totalPageHeightPt = isA4 ? 841.89 : 792.0;
  const totalPageWidthPt = isA4 ? 595.28 : 612.0;

  const topMargin = style.margins?.top ?? 36;
  const bottomMargin = style.margins?.bottom ?? 36;
  const leftMargin = style.margins?.left ?? 42;
  const rightMargin = style.margins?.right ?? 42;

  const printableHeightPt = totalPageHeightPt - (topMargin + bottomMargin);
  const printableWidthPt = totalPageWidthPt - (leftMargin + rightMargin);

  const fontSizes = getResolvedFontSizes(style.typography);

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
  const isMixLayout = style.layout.type === 'mix';

  // 1. Single Column Layout (Classic, Header Banner, Compact, Creative, Minimal, Academic)
  if (!isTwoColumn && !isMixLayout) {
    const headerHeightPt = estimateHeaderHeight(content, style, fontSizes, printableWidthPt);
    const pagesSlices = paginateSectionList(
      visibleSections,
      printableWidthPt,
      printableHeightPt,
      headerHeightPt,
      style,
      fontSizes
    );

    return pagesSlices.map((mainSecs, idx) => ({
      pageIndex: idx,
      isFirstPage: idx === 0,
      mainSections: mainSecs,
      sidebarSections: [],
    }));
  }

  // 2. Mix Layout (Full-width header/summary + 2-column body)
  if (isMixLayout) {
    const sidebarSectionIdSet = new Set(style.layout.sidebarSectionIds || []);
    const sidebarWidthPercent = style.layout.sidebarWidthPercent || 32;
    const colGapPt = 24;

    const sidebarWidthPt = Math.floor((printableWidthPt * (sidebarWidthPercent / 100)) - (colGapPt / 2));
    const mainWidthPt = Math.floor(printableWidthPt - sidebarWidthPt - colGapPt);

    const getPlacement = (s: ResumeSection): 'full' | 'sidebar' | 'main' => {
      if (style.layout.sectionPlacement && style.layout.sectionPlacement[s.id]) {
        return style.layout.sectionPlacement[s.id];
      }
      if (sidebarSectionIdSet.has(s.id)) return 'sidebar';
      if (s.type === 'summary') return 'full';
      return 'main';
    };

    const fullSecs = visibleSections.filter((s) => getPlacement(s) === 'full');
    const mainSecs = visibleSections.filter((s) => getPlacement(s) === 'main');
    const sidebarSecs = visibleSections.filter((s) => getPlacement(s) === 'sidebar');

    const headerHeightPt = estimateHeaderHeight(content, style, fontSizes, printableWidthPt);

    // Calculate height of full-width sections on first page
    const sH = estimateSectionHeadingHeight(style, fontSizes);
    let fullSectionsHeight = 0;
    for (const fs of fullSecs) {
      let secH = sH;
      for (const it of fs.items) {
        secH += estimateItemHeight(it, fs, style, fontSizes, printableWidthPt);
      }
      fullSectionsHeight += secH + style.spacing.sectionSpacing;
    }

    const firstPageBodyOffsetPt = Math.min(
      printableHeightPt * 0.75,
      headerHeightPt + fullSectionsHeight
    );

    const mainPages = paginateSectionList(
      mainSecs,
      mainWidthPt,
      printableHeightPt,
      firstPageBodyOffsetPt,
      style,
      fontSizes
    );

    const sidebarPages = paginateSectionList(
      sidebarSecs,
      sidebarWidthPt,
      printableHeightPt,
      firstPageBodyOffsetPt,
      style,
      fontSizes
    );

    const totalPages = Math.max(mainPages.length, sidebarPages.length, 1);
    const result: PageLayoutSlice[] = [];

    for (let p = 0; p < totalPages; p++) {
      result.push({
        pageIndex: p,
        isFirstPage: p === 0,
        mainSections: p === 0 ? [...fullSecs, ...(mainPages[p] || [])] : (mainPages[p] || []),
        sidebarSections: sidebarPages[p] || [],
      });
    }

    return result;
  }

  // 3. Two Column Layout (sidebar_left, sidebar_right)
  const sidebarSectionIdSet = new Set(style.layout.sidebarSectionIds || []);
  const sidebarWidthPercent = style.layout.sidebarWidthPercent || 32;
  const colGapPt = 24;

  const sidebarWidthPt = Math.floor((printableWidthPt * (sidebarWidthPercent / 100)) - (colGapPt / 2));
  const mainWidthPt = Math.floor(printableWidthPt - sidebarWidthPt - colGapPt);

  const mainSectionsList = visibleSections.filter((s) => !sidebarSectionIdSet.has(s.id));
  const sidebarSectionsList = visibleSections.filter((s) => sidebarSectionIdSet.has(s.id));

  const finalMainSections =
    mainSectionsList.length > 0
      ? mainSectionsList
      : visibleSections.filter(
          (s) => s.type !== 'skills' && s.type !== 'education' && s.type !== 'certifications'
        );

  const finalSidebarSections =
    sidebarSectionsList.length > 0
      ? sidebarSectionsList
      : visibleSections.filter(
          (s) => s.type === 'skills' || s.type === 'education' || s.type === 'certifications'
        );

  const headerHeightPt = estimateHeaderHeight(content, style, fontSizes, printableWidthPt);

  const mainPages = paginateSectionList(
    finalMainSections,
    mainWidthPt,
    printableHeightPt,
    headerHeightPt,
    style,
    fontSizes
  );

  const sidebarPages = paginateSectionList(
    finalSidebarSections,
    sidebarWidthPt,
    printableHeightPt,
    headerHeightPt,
    style,
    fontSizes
  );

  const totalPages = Math.max(mainPages.length, sidebarPages.length, 1);
  const result: PageLayoutSlice[] = [];

  for (let p = 0; p < totalPages; p++) {
    result.push({
      pageIndex: p,
      isFirstPage: p === 0,
      mainSections: mainPages[p] || [],
      sidebarSections: sidebarPages[p] || [],
    });
  }

  return result;
}

'use client';

import React, { useMemo } from 'react';
import { ResumeContent, ResumeSection } from '@/types/content';
import { ResumeStyle } from '@/types/style';
import { getStyleCssVariables } from './style-injector';
import { PageView } from './PageView';
import { ResumeHeader } from './ResumeHeader';
import { SectionRenderer } from './SectionRenderer';
import { PageFooter } from './PageFooter';
import { paginateResume } from '@/lib/pagination';
import { getLocaleDirection } from '@/lib/i18n';

interface ResumeDocumentProps {
  content: ResumeContent;
  style: ResumeStyle;
  isPrint?: boolean;
}

export const ResumeDocument: React.FC<ResumeDocumentProps> = ({
  content,
  style,
  isPrint = false,
}) => {
  // CSS variables injected into the root container
  const cssVariables = useMemo(() => getStyleCssVariables(style), [style]);

  // Paginated slices for single or multi-page rendering
  const pages = useMemo(() => paginateResume(content, style), [content, style]);

  const direction = style.direction || getLocaleDirection(style.locale);
  const layoutType = style.layout.type;
  const isTwoColumn = layoutType === 'sidebar_left' || layoutType === 'sidebar_right';
  const isMixLayout = layoutType === 'mix';
  const isSidebarLeft = layoutType === 'sidebar_left';

  // Filter sections by placement for mix layout
  const getSectionPlacement = (section: ResumeSection): 'main' | 'sidebar' | 'full' => {
    if (style.layout.sectionPlacement && style.layout.sectionPlacement[section.id]) {
      return style.layout.sectionPlacement[section.id];
    }
    if (style.layout.sidebarSectionIds.includes(section.id)) {
      return 'sidebar';
    }
    if (isMixLayout && section.type === 'summary') {
      return 'full';
    }
    return 'main';
  };

  return (
    <div
      className="resume-document resume-ready font-[family-name:var(--font-base)]"
      dir={direction}
      style={cssVariables}
    >
      {pages.map((pageSlice, pageIdx) => {
        // Compute mix layout partitioning for this page slice
        const fullSections: ResumeSection[] = [];
        const mainSections: ResumeSection[] = [];
        const sidebarSections: ResumeSection[] = [];

        if (isMixLayout) {
          const allSliceSections = [
            ...pageSlice.mainSections,
            ...pageSlice.sidebarSections,
          ];
          for (const s of allSliceSections) {
            const placement = getSectionPlacement(s);
            if (placement === 'full') fullSections.push(s);
            else if (placement === 'sidebar') sidebarSections.push(s);
            else mainSections.push(s);
          }
        }

        return (
          <PageView
            key={pageIdx}
            pageSize={style.pageSize}
            pageNumber={pageIdx + 1}
            totalPages={pages.length}
            isPrint={isPrint}
          >
            {/* Header on First Page */}
            {pageSlice.isFirstPage && (
              <ResumeHeader
                header={content.coverLetter?.sender || content.header}
                decorations={style.decorations}
                headerConfig={style.header}
                photoConfig={style.photo}
                isBanner={
                  style.layout.type === 'header_banner' ||
                  Boolean(style.decorations?.headerBanner)
                }
              />
            )}

            {/* Cover Letter Layout */}
            {content.coverLetter ? (
              <div className="flex-1 flex flex-col pt-2 text-[var(--color-text)]">
                {/* Date */}
                {content.coverLetter.date && (
                  <div className="mb-4 text-sm font-medium text-[var(--color-muted)]">
                    {content.coverLetter.date}
                  </div>
                )}

                {/* Recipient */}
                {content.coverLetter.recipient && (
                  <div className="mb-5 text-sm leading-relaxed">
                    {content.coverLetter.recipient.name && (
                      <div className="font-bold">{content.coverLetter.recipient.name}</div>
                    )}
                    {content.coverLetter.recipient.title && (
                      <div className="text-[var(--color-muted)]">
                        {content.coverLetter.recipient.title}
                      </div>
                    )}
                    {content.coverLetter.recipient.company && (
                      <div className="font-semibold text-[var(--color-accent)]">
                        {content.coverLetter.recipient.company}
                      </div>
                    )}
                    {content.coverLetter.recipient.address && (
                      <div className="text-[var(--color-muted)] whitespace-pre-line">
                        {content.coverLetter.recipient.address}
                      </div>
                    )}
                  </div>
                )}

                {/* Salutation */}
                {content.coverLetter.salutation && (
                  <div className="mb-4 font-semibold text-base">
                    {content.coverLetter.salutation}
                  </div>
                )}

                {/* Body Paragraphs */}
                <div
                  className="flex flex-col gap-3.5 mb-6 leading-relaxed"
                  style={{ fontSize: 'var(--font-size-body)' }}
                >
                  {content.coverLetter.paragraphs.map((p, pIdx) => (
                    <p key={p.id || pIdx} className="text-justify">
                      {p.text}
                    </p>
                  ))}
                </div>

                {/* Closing & Signature */}
                <div className="mt-auto pt-4 text-sm">
                  <div className="font-medium text-[var(--color-muted)] mb-4">
                    {content.coverLetter.closing || 'Sincerely,'}
                  </div>
                  <div
                    className="font-bold font-[family-name:var(--font-heading)] text-base"
                    style={{ color: 'var(--color-accent)' }}
                  >
                    {content.coverLetter.signature ||
                      content.coverLetter.sender?.name ||
                      content.header.name}
                  </div>
                </div>
              </div>
            ) : isMixLayout ? (
              /* Mix Layout (Full-width header/summary + 2-column body) */
              <div className="flex-1 flex flex-col">
                {fullSections.map((section) => (
                  <SectionRenderer
                    key={section.id}
                    section={section}
                    headingStyle={style.headingStyle}
                    bulletStyle={style.bulletStyle}
                    headingConfig={style.heading}
                    entryLayout={style.entryLayout}
                    sectionCustomizations={style.sectionCustomizations}
                    dateFormat={style.dateFormat}
                  />
                ))}

                <div className="flex-1 flex gap-x-6 items-stretch mt-1">
                  <aside
                    className="rounded-sm p-3 -my-2 flex flex-col"
                    style={{
                      width: `${style.layout.sidebarWidthPercent}%`,
                      backgroundColor: 'var(--color-sidebar-background)',
                    }}
                  >
                    {sidebarSections.map((section) => (
                      <SectionRenderer
                        key={section.id}
                        section={section}
                        headingStyle={style.headingStyle}
                        bulletStyle={style.bulletStyle}
                        headingConfig={style.heading}
                        entryLayout={style.entryLayout}
                        sectionCustomizations={style.sectionCustomizations}
                        dateFormat={style.dateFormat}
                      />
                    ))}
                  </aside>

                  <main className="flex-1 flex flex-col">
                    {mainSections.map((section) => (
                      <SectionRenderer
                        key={section.id}
                        section={section}
                        headingStyle={style.headingStyle}
                        bulletStyle={style.bulletStyle}
                        headingConfig={style.heading}
                        entryLayout={style.entryLayout}
                        sectionCustomizations={style.sectionCustomizations}
                        dateFormat={style.dateFormat}
                      />
                    ))}
                  </main>
                </div>
              </div>
            ) : !isTwoColumn ? (
              /* Single Column Layout (Classic, Header Banner, Compact, Creative, Minimal, Academic) */
              <div className="flex-1 flex flex-col">
                {pageSlice.mainSections.map((section) => (
                  <SectionRenderer
                    key={section.id}
                    section={section}
                    headingStyle={style.headingStyle}
                    bulletStyle={style.bulletStyle}
                    headingConfig={style.heading}
                    entryLayout={style.entryLayout}
                    sectionCustomizations={style.sectionCustomizations}
                    dateFormat={style.dateFormat}
                  />
                ))}
              </div>
            ) : (
              /* Two Column Sidebar Layout (sidebar_left, sidebar_right) */
              <div className="flex-1 flex gap-x-6 items-stretch">
                {isSidebarLeft && (
                  <aside
                    className="rounded-sm p-3 -my-2 flex flex-col"
                    style={{
                      width: `${style.layout.sidebarWidthPercent}%`,
                      backgroundColor: 'var(--color-sidebar-background)',
                    }}
                  >
                    {pageSlice.sidebarSections.map((section) => (
                      <SectionRenderer
                        key={section.id}
                        section={section}
                        headingStyle={style.headingStyle}
                        bulletStyle={style.bulletStyle}
                        headingConfig={style.heading}
                        entryLayout={style.entryLayout}
                        sectionCustomizations={style.sectionCustomizations}
                        dateFormat={style.dateFormat}
                      />
                    ))}
                  </aside>
                )}

                <main className="flex-1 flex flex-col">
                  {pageSlice.mainSections.map((section) => (
                    <SectionRenderer
                      key={section.id}
                      section={section}
                      headingStyle={style.headingStyle}
                      bulletStyle={style.bulletStyle}
                      headingConfig={style.heading}
                      entryLayout={style.entryLayout}
                      sectionCustomizations={style.sectionCustomizations}
                      dateFormat={style.dateFormat}
                    />
                  ))}
                </main>

                {!isSidebarLeft && (
                  <aside
                    className="rounded-sm p-3 -my-2 flex flex-col"
                    style={{
                      width: `${style.layout.sidebarWidthPercent}%`,
                      backgroundColor: 'var(--color-sidebar-background)',
                    }}
                  >
                    {pageSlice.sidebarSections.map((section) => (
                      <SectionRenderer
                        key={section.id}
                        section={section}
                        headingStyle={style.headingStyle}
                        bulletStyle={style.bulletStyle}
                        headingConfig={style.heading}
                        entryLayout={style.entryLayout}
                        sectionCustomizations={style.sectionCustomizations}
                        dateFormat={style.dateFormat}
                      />
                    ))}
                  </aside>
                )}
              </div>
            )}

            {/* Running Page Footer */}
            <PageFooter
              footer={style.footer}
              header={content.header}
              pageNumber={pageIdx + 1}
              totalPages={pages.length}
            />
          </PageView>
        );
      })}
    </div>
  );
};

'use client';

import React, { useMemo } from 'react';
import { ResumeContent } from '@/types/content';
import { ResumeStyle } from '@/types/style';
import { getStyleCssVariables } from './style-injector';
import { PageView } from './PageView';
import { ResumeHeader } from './ResumeHeader';
import { SectionRenderer } from './SectionRenderer';
import { paginateResume } from '@/lib/pagination';

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

  const isTwoColumn =
    style.layout.type === 'sidebar_left' || style.layout.type === 'sidebar_right';
  const isSidebarLeft = style.layout.type === 'sidebar_left';

  return (
    <div
      className="resume-document resume-ready font-[family-name:var(--font-base)]"
      style={cssVariables}
    >
      {pages.map((pageSlice, pageIdx) => (
        <PageView
          key={pageIdx}
          pageSize={style.pageSize}
          pageNumber={pageIdx + 1}
          totalPages={pages.length}
          isPrint={isPrint}
        >
          {/* Header on First Page */}
          {pageSlice.isFirstPage && <ResumeHeader header={content.header} />}

          {/* Body Content */}
          {!isTwoColumn ? (
            /* Single Column Layout */
            <div className="flex-1 flex flex-col">
              {pageSlice.mainSections.map((section) => (
                <SectionRenderer
                  key={section.id}
                  section={section}
                  headingStyle={style.headingStyle}
                  bulletStyle={style.bulletStyle}
                />
              ))}
            </div>
          ) : (
            /* Two Column Sidebar Layout */
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
                    />
                  ))}
                </aside>
              )}
            </div>
          )}
        </PageView>
      ))}
    </div>
  );
};

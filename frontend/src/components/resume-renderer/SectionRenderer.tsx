import React from 'react';
import { ResumeSection, SectionItem, BulletItem } from '@/types/content';
import { HeadingStyle, BulletStyle } from '@/types/style';

interface SectionRendererProps {
  section: ResumeSection;
  headingStyle: HeadingStyle;
  bulletStyle: BulletStyle;
}

/**
 * Safely parse safe inline markup (**bold**, *italic*, [label](url)) into React nodes.
 * Eliminates XSS risk without requiring dangerouslySetInnerHTML.
 */
export function renderInlineMarkup(rawText: string): React.ReactNode {
  if (!rawText) return null;

  // Pattern matches:
  // 1: **bold**
  // 2: *italic*
  // 3: [link text](url)
  const tokens = rawText.split(/(\*\*[\s\S]+?\*\*|\*[^\s\*][\s\S]*?\*|\[[\s\S]+?\]\([^\s\)]+?\))/g);

  return tokens.map((token, idx) => {
    if (token.startsWith('**') && token.endsWith('**') && token.length >= 4) {
      return (
        <strong key={idx} className="font-semibold text-[var(--color-text)]">
          {token.slice(2, -2)}
        </strong>
      );
    }
    if (token.startsWith('*') && token.endsWith('*') && token.length >= 2 && !token.startsWith('**')) {
      return (
        <em key={idx} className="italic">
          {token.slice(1, -1)}
        </em>
      );
    }
    const linkMatch = token.match(/^\[([\s\S]+?)\]\(([^\s\)]+?)\)$/);
    if (linkMatch) {
      const [, label, href] = linkMatch;
      return (
        <a
          key={idx}
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="underline hover:text-[var(--color-accent)] transition-colors"
        >
          {label}
        </a>
      );
    }
    return token;
  });
}

export const SectionRenderer: React.FC<SectionRendererProps> = ({
  section,
  headingStyle,
  bulletStyle,
}) => {
  if (section.visible === false || !section.items || section.items.length === 0) {
    return null;
  }

  // Filter out items explicitly marked hidden
  const visibleItems = section.items.filter((item) => item.visible !== false);
  if (visibleItems.length === 0) {
    return null;
  }

  // Heading style decoration
  const getHeadingClasses = () => {
    switch (headingStyle) {
      case 'underline':
        return 'border-b-2 border-[var(--color-accent)] pb-1 mb-2 font-bold';
      case 'bar':
        return 'border-l-4 rtl:border-l-0 rtl:border-r-4 border-[var(--color-accent)] pl-2 rtl:pl-0 rtl:pr-2 mb-2 font-bold';
      case 'caps':
        return 'uppercase tracking-wider border-b border-[var(--color-divider)] pb-1 mb-2 font-semibold text-[var(--color-accent)]';
      case 'boxed':
        return 'bg-[var(--color-accent)] text-white px-2.5 py-0.5 rounded font-bold inline-block mb-2 shadow-xs';
      case 'pill':
        return 'bg-[var(--color-accent)]/10 text-[var(--color-accent)] border border-[var(--color-accent)]/30 px-3 py-0.5 rounded-full font-bold inline-block mb-2';
      case 'plain':
      default:
        return 'mb-1.5 font-bold text-[var(--color-text)]';
    }
  };

  const renderBulletMarker = () => {
    switch (bulletStyle) {
      case 'disc':
        return <span className="text-[var(--color-accent)] mr-2 select-none">•</span>;
      case 'circle':
        return <span className="text-[var(--color-accent)] mr-2 select-none">◦</span>;
      case 'square':
        return <span className="text-[var(--color-accent)] mr-2 select-none">▪</span>;
      case 'dash':
        return <span className="text-[var(--color-accent)] mr-2 select-none">–</span>;
      case 'arrow':
        return <span className="text-[var(--color-accent)] mr-2 select-none">➤</span>;
      case 'none':
      default:
        return null;
    }
  };

  const isTagsSection =
    section.type === 'skills' ||
    section.type === 'interests' ||
    section.items.some((i) => i.itemType === 'tags');

  return (
    <section
      className="resume-section"
      style={{
        marginBottom: 'var(--spacing-section)',
      }}
    >
      {/* Section Title */}
      <h2
        className={`font-[family-name:var(--font-heading)] leading-none text-[var(--color-text)] ${getHeadingClasses()}`}
        style={{ fontSize: 'var(--font-size-sectionHeading, var(--font-size-section-heading))' }}
      >
        {section.title}
      </h2>

      {/* Section Items */}
      <div className="flex flex-col">
        {visibleItems.map((item, itemIdx) => {
          const isItemTags = item.itemType === 'tags' || isTagsSection;
          const isParagraph = item.itemType === 'paragraph' || section.type === 'summary';

          return (
            <div
              key={item.id || itemIdx}
              className="resume-item"
              style={{
                marginBottom:
                  itemIdx === visibleItems.length - 1
                    ? 0
                    : 'var(--spacing-item)',
              }}
            >
              {/* Item Title & Subtitle + Meta */}
              {(item.title || item.subtitle || item.dateRange || item.location) && (
                <div className="flex justify-between items-baseline flex-wrap gap-x-2 leading-tight">
                  <div className="flex flex-wrap items-baseline gap-x-1.5">
                    {item.title && (
                      <span
                        className="font-bold text-[var(--color-text)]"
                        style={{ fontSize: 'var(--font-size-item-title)' }}
                      >
                        {renderInlineMarkup(item.title)}
                      </span>
                    )}
                    {item.title && item.subtitle && (
                      <span className="text-[var(--color-muted)] text-xs select-none">|</span>
                    )}
                    {item.subtitle && (
                      <span
                        className="font-medium text-[var(--color-text)]"
                        style={{ fontSize: 'var(--font-size-item-subtitle)' }}
                      >
                        {renderInlineMarkup(item.subtitle)}
                      </span>
                    )}
                  </div>

                  {/* Right aligned Meta: Date & Location */}
                  <div
                    className="text-right rtl:text-left text-[var(--color-muted)] whitespace-nowrap ms-auto"
                    style={{ fontSize: 'var(--font-size-meta)' }}
                  >
                    {item.dateRange && <span>{item.dateRange}</span>}
                    {item.dateRange && item.location && <span>, </span>}
                    {item.location && <span>{item.location}</span>}
                  </div>
                </div>
              )}

              {/* Tag Badges Variant */}
              {isItemTags && item.bullets && item.bullets.length > 0 && !isParagraph && (
                <div className="mt-1 flex flex-wrap gap-1.5">
                  {item.bullets.map((bullet, bIdx) => {
                    // Bullets in skills might be comma-separated or single tags
                    const tags = bullet.text.split(/,\s*/);
                    return tags.map((tag, tIdx) => (
                      <span
                        key={`${bullet.id || bIdx}-${tIdx}`}
                        className="px-2 py-0.5 rounded text-xs border border-[var(--color-divider)] bg-[var(--color-sidebar-background)] text-[var(--color-text)]"
                        style={{ fontSize: 'var(--font-size-body)' }}
                      >
                        {renderInlineMarkup(tag.trim())}
                      </span>
                    ));
                  })}
                </div>
              )}

              {/* Paragraph Variant */}
              {isParagraph && item.bullets && item.bullets.length > 0 && (
                <div className="mt-1 leading-relaxed text-[var(--color-text)]" style={{ fontSize: 'var(--font-size-body)' }}>
                  {item.bullets.map((b) => renderInlineMarkup(b.text))}
                </div>
              )}

              {/* Standard List Bullets Variant */}
              {!isItemTags && !isParagraph && item.bullets && item.bullets.length > 0 && (
                <div className="mt-1 flex flex-col">
                  {item.bullets.map((bullet, bIdx) => {
                    const indentClass =
                      bullet.level === 1 ? 'ml-4' : bullet.level === 2 ? 'ml-8' : '';

                    return (
                      <div
                        key={bullet.id || bIdx}
                        className={`flex items-start leading-snug ${indentClass}`}
                        style={{
                          marginBottom:
                            bIdx === item.bullets.length - 1
                              ? 0
                              : 'var(--spacing-bullet)',
                        }}
                      >
                        {renderBulletMarker()}
                        <span
                          className="text-[var(--color-text)] flex-1"
                          style={{ fontSize: 'var(--font-size-body)' }}
                        >
                          {renderInlineMarkup(bullet.text)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
};

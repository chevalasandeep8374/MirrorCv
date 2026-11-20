import React from 'react';
import { ResumeSection, SectionItem, BulletItem } from '@/types/content';
import {
  HeadingStyle,
  BulletStyle,
  HeadingConfig,
  EntryLayoutConfig,
  SectionCustomizations,
} from '@/types/style';
import { formatStructuredDate } from '@/lib/migration';

interface SectionRendererProps {
  section: ResumeSection;
  headingStyle: HeadingStyle;
  bulletStyle: BulletStyle;
  headingConfig?: HeadingConfig;
  entryLayout?: EntryLayoutConfig;
  sectionCustomizations?: SectionCustomizations;
  dateFormat?: string;
}

/**
 * Safely parse safe inline markup (**bold**, *italic*, [label](url)) into React nodes.
 * Eliminates XSS risk without requiring dangerouslySetInnerHTML.
 */
export function renderInlineMarkup(rawText: string): React.ReactNode {
  if (!rawText) return null;

  const tokens = rawText.split(
    /(\*\*[\s\S]+?\*\*|\*[^\s\*][\s\S]*?\*|\[[\s\S]+?\]\([^\s\)]+?\))/g
  );

  return tokens.map((token, idx) => {
    if (token.startsWith('**') && token.endsWith('**') && token.length >= 4) {
      return (
        <strong key={idx} className="font-semibold text-[var(--color-text)]">
          {token.slice(2, -2)}
        </strong>
      );
    }
    if (
      token.startsWith('*') &&
      token.endsWith('*') &&
      token.length >= 2 &&
      !token.startsWith('**')
    ) {
      return (
        <em key={idx} className="italic">
          {token.slice(1, -1)}
        </em>
      );
    }
    const linkMatch = token.match(/^\[([\s\S]+?)\]\(([^\s\)]+?)\)$/);
    if (linkMatch) {
      const [, label, rawHref] = linkMatch;
      const cleanHref = (rawHref || '').trim();
      const lower = cleanHref.toLowerCase();
      // Security: Strictly reject javascript:, data:, and vbscript: URIs
      const isDangerous = lower.startsWith('javascript:') || lower.startsWith('data:') || lower.startsWith('vbscript:');
      const safeHref = isDangerous ? '#' : cleanHref;
      return (
        <a
          key={idx}
          href={safeHref}
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
  headingConfig,
  entryLayout,
  sectionCustomizations,
  dateFormat = 'MMM YYYY',
}) => {
  if (section.visible === false || !section.items || section.items.length === 0) {
    return null;
  }

  // Filter out items explicitly marked hidden
  const visibleItems = section.items.filter((item) => item.visible !== false);
  if (visibleItems.length === 0) {
    return null;
  }

  // Heading Capitalization
  const capitalizationClass =
    headingConfig?.capitalization === 'uppercase'
      ? 'uppercase tracking-wider'
      : headingConfig?.capitalization === 'capitalize'
      ? 'capitalize'
      : '';

  // Heading style decoration
  const getHeadingClasses = () => {
    switch (headingStyle) {
      case 'underline':
        return 'border-b-2 border-[var(--accent-headings-line,var(--color-accent))] pb-1 mb-2 font-bold';
      case 'bar':
        return 'border-l-4 rtl:border-l-0 rtl:border-r-4 border-[var(--accent-headings-line,var(--color-accent))] pl-2 rtl:pl-0 rtl:pr-2 mb-2 font-bold';
      case 'side_line':
        return 'border-l-4 rtl:border-l-0 rtl:border-r-4 border-[var(--accent-headings-line,var(--color-accent))] pl-3 rtl:pl-0 rtl:pr-3 py-0.5 mb-2 font-bold';
      case 'caps':
        return 'uppercase tracking-wider border-b border-[var(--color-divider)] pb-1 mb-2 font-semibold';
      case 'boxed':
        return 'bg-[var(--color-accent)] text-white px-2.5 py-0.5 rounded font-bold inline-block mb-2 shadow-xs';
      case 'pill':
        return 'bg-[var(--color-accent)]/10 text-[var(--color-accent)] border border-[var(--color-accent)]/30 px-3 py-0.5 rounded-full font-bold inline-block mb-2';
      case 'plain':
      default:
        return 'mb-1.5 font-bold';
    }
  };

  const renderBulletMarker = () => {
    switch (bulletStyle) {
      case 'disc':
        return <span className="text-[var(--accent-bullets,var(--color-accent))] mr-2 select-none">•</span>;
      case 'circle':
        return <span className="text-[var(--accent-bullets,var(--color-accent))] mr-2 select-none">◦</span>;
      case 'square':
        return <span className="text-[var(--accent-bullets,var(--color-accent))] mr-2 select-none">▪</span>;
      case 'dash':
        return <span className="text-[var(--accent-bullets,var(--color-accent))] mr-2 select-none">–</span>;
      case 'arrow':
        return <span className="text-[var(--accent-bullets,var(--color-accent))] mr-2 select-none">➤</span>;
      case 'none':
      default:
        return null;
    }
  };

  const isTagsSection =
    section.type === 'skills' ||
    section.type === 'interests' ||
    section.type === 'languages' ||
    section.items.some((i) => i.itemType === 'tags');

  const skillsCust = sectionCustomizations?.skills;
  const rawSkillsMode = skillsCust?.style || 'rows';
  const skillsMode = rawSkillsMode === 'normal' ? 'rows' : rawSkillsMode;
  const isSkillsNormalText = skillsMode === 'rows';
  const isSkillsStackedText = skillsMode === 'stacked';
  const startRowsWithBullets = skillsCust?.startRowsWithBullets ?? false;
  const subInfoStyle = skillsCust?.subInfoStyle || 'colon';
  const rowSpacing = skillsCust?.rowSpacing || 'tight';

  // Section specific ordering: experience or education title/subtitle inversion
  const isSubtitleFirst =
    (section.type === 'experience' &&
      sectionCustomizations?.experience?.titleSubtitleOrder === 'subtitle_first') ||
    (section.type === 'education' &&
      sectionCustomizations?.education?.titleSubtitleOrder === 'subtitle_first');

  const isDateBelowTitle = entryLayout?.dateLocationPosition === 'below_title';

  // Render Proficiency dots (1-5)
  const renderProficiency = (level: number) => (
    <span className="inline-flex items-center gap-1 ml-2 select-none">
      {[1, 2, 3, 4, 5].map((dot) => (
        <span
          key={dot}
          className={`w-1.5 h-1.5 rounded-full ${
            dot <= level ? 'bg-[var(--color-accent)]' : 'bg-[var(--color-divider)]'
          }`}
        />
      ))}
    </span>
  );

  return (
    <section
      className="resume-section"
      style={{
        marginBottom: 'var(--spacing-section)',
      }}
    >
      {/* Section Title */}
      <h2
        className={`font-[family-name:var(--font-heading)] leading-none text-[var(--accent-headings,var(--color-text))] ${getHeadingClasses()} ${capitalizationClass}`}
        style={{ fontSize: 'var(--font-size-section-heading)' }}
      >
        {section.title}
      </h2>

      {/* Section Items */}
      {section.type === 'certifications' &&
      visibleItems.every(
        (it) => !it.dateRange && !it.subtitle && !it.location && (!it.bullets || it.bullets.length === 0)
      ) ? (
        <div
          className="grid grid-cols-2 gap-x-6 gap-y-1 text-[var(--color-text)]"
          style={{ fontSize: 'var(--font-size-body)' }}
        >
          {visibleItems.map((item, itemIdx) => (
            <div key={item.id || itemIdx} className="resume-item flex items-baseline leading-snug">
              <span className="text-[var(--accent-bullets,var(--color-accent))] mr-2 select-none font-bold">•</span>
              <span className="text-[var(--color-text)]">
                {renderInlineMarkup(item.title)}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <div className="flex flex-col">
          {visibleItems.map((item, itemIdx) => {
            const isItemTags = item.itemType === 'tags' || isTagsSection;
          const isParagraph = item.itemType === 'paragraph' || section.type === 'summary';

          // Format structured dates or fallback to dateRange
          const displayDate =
            (item.dates && (item.dates.startYear || item.dates.isCurrent))
              ? formatStructuredDate(item.dates, dateFormat)
              : item.dateRange;

          // Header fields: first & second based on order setting
          const firstField = isSubtitleFirst ? item.subtitle : item.title;
          const secondField = isSubtitleFirst ? item.title : item.subtitle;

          // Extract clean skill list for normal text formatting
          const skillsList = (item.bullets || []).flatMap((bullet) =>
            bullet.text
              .split(/,\s*/)
              .map((s) => s.trim())
              .filter(Boolean)
          );

          // Skills: Normal Text (Inline Category: Skills)
          if (section.type === 'skills' && isSkillsNormalText) {
            return (
              <div
                key={item.id || itemIdx}
                className="resume-item leading-relaxed"
                style={{
                  marginBottom:
                    itemIdx === visibleItems.length - 1
                      ? 0
                      : rowSpacing === 'spacious'
                      ? 'var(--spacing-item)'
                      : 'calc(var(--spacing-item) * 0.55)',
                }}
              >
                <div
                  className="flex items-baseline flex-wrap gap-x-1.5 text-[var(--color-text)]"
                  style={{ fontSize: 'var(--font-size-body)' }}
                >
                  {startRowsWithBullets && (
                    <span className="text-[var(--accent-bullets,var(--color-accent))] select-none mr-0.5 font-bold">
                      {renderBulletMarker() || '•'}
                    </span>
                  )}
                  {firstField && (
                    <span
                      className="font-bold text-[var(--accent-entry-title,var(--color-text))] shrink-0"
                      style={{ fontSize: 'var(--font-size-item-title, var(--font-size-body))' }}
                    >
                      {renderInlineMarkup(firstField)}
                      {subInfoStyle === 'dash'
                        ? ' — '
                        : subInfoStyle === 'bracket'
                        ? ' ('
                        : ': '}
                    </span>
                  )}
                  <span className="text-[var(--color-text)]">
                    {skillsList.map((skill, sIdx) => (
                      <React.Fragment key={sIdx}>
                        {sIdx > 0 && ', '}
                        <span>{renderInlineMarkup(skill)}</span>
                      </React.Fragment>
                    ))}
                    {firstField && subInfoStyle === 'bracket' ? ')' : ''}
                  </span>

                  {(secondField || displayDate || item.location) && (
                    <span
                      className="text-[var(--accent-dates,var(--color-muted))] text-xs ms-auto whitespace-nowrap"
                      style={{ fontSize: 'var(--font-size-meta)' }}
                    >
                      {secondField && <span>{secondField} </span>}
                      {displayDate && <span>{displayDate} </span>}
                      {item.location && <span>({item.location})</span>}
                    </span>
                  )}
                </div>
              </div>
            );
          }

          // Skills: Normal Text (Stacked: Category on top, comma-separated plain text below)
          if (section.type === 'skills' && isSkillsStackedText) {
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
                <div className="leading-tight flex justify-between items-baseline flex-wrap gap-x-2">
                  {firstField && (
                    <span
                      className="font-bold text-[var(--accent-entry-title,var(--color-text))]"
                      style={{ fontSize: 'var(--font-size-item-title)' }}
                    >
                      {renderInlineMarkup(firstField)}
                    </span>
                  )}
                  {(displayDate || item.location) && (
                    <span
                      className="text-[var(--accent-dates,var(--color-muted))] text-xs ms-auto whitespace-nowrap"
                      style={{ fontSize: 'var(--font-size-meta)' }}
                    >
                      {displayDate && <span>{displayDate}</span>}
                      {displayDate && item.location && <span>, </span>}
                      {item.location && <span>{item.location}</span>}
                    </span>
                  )}
                </div>
                <div
                  className="mt-0.5 text-[var(--color-text)] leading-relaxed"
                  style={{ fontSize: 'var(--font-size-body)' }}
                >
                  {skillsList.map((skill, sIdx) => (
                    <React.Fragment key={sIdx}>
                      {sIdx > 0 && ', '}
                      <span>{renderInlineMarkup(skill)}</span>
                    </React.Fragment>
                  ))}
                </div>
              </div>
            );
          }

          return (
            <div
              key={item.id || itemIdx}
              className="resume-item"
              style={{
                marginBottom:
                  itemIdx === visibleItems.length - 1 ? 0 : 'var(--spacing-item)',
              }}
            >
              {/* Item Title & Subtitle + Meta */}
              {(firstField || secondField || displayDate || item.location) && (
                <div
                  className={`leading-tight ${
                    isDateBelowTitle
                      ? 'flex flex-col gap-0.5'
                      : 'flex justify-between items-baseline flex-wrap gap-x-2'
                  }`}
                >
                  <div className="flex flex-wrap items-baseline gap-x-1.5">
                    {firstField && (
                      <span
                        className="font-bold text-[var(--accent-entry-title,var(--color-text))]"
                        style={{ fontSize: 'var(--font-size-item-title)' }}
                      >
                        {renderInlineMarkup(firstField)}
                      </span>
                    )}
                    {firstField && secondField && (
                      <span className="text-[var(--color-muted)] text-xs select-none">|</span>
                    )}
                    {secondField && (
                      <span
                        className="font-medium text-[var(--accent-entry-subtitle,var(--color-text))]"
                        style={{ fontSize: 'var(--font-size-item-subtitle)' }}
                      >
                        {renderInlineMarkup(secondField)}
                      </span>
                    )}
                  </div>

                  {/* Meta: Date & Location */}
                  <div
                    className={`text-[var(--accent-dates,var(--color-muted))] whitespace-nowrap ${
                      isDateBelowTitle ? 'text-xs' : 'text-right rtl:text-left ms-auto'
                    }`}
                    style={{ fontSize: 'var(--font-size-meta)' }}
                  >
                    {displayDate && <span>{displayDate}</span>}
                    {displayDate && item.location && <span>, </span>}
                    {item.location && <span>{item.location}</span>}
                  </div>
                </div>
              )}

              {/* Tag Badges Variant for Skills / Languages / Interests */}
              {isItemTags && item.bullets && item.bullets.length > 0 && !isParagraph && (
                <div
                  className={`mt-1 flex flex-wrap gap-1.5 ${
                    skillsMode === 'grid' ? 'grid grid-cols-2 sm:grid-cols-3 gap-2' : ''
                  }`}
                >
                  {item.bullets.map((bullet, bIdx) => {
                    const tags = bullet.text.split(/,\s*/);
                    return tags.map((tag, tIdx) => (
                      <span
                        key={`${bullet.id || bIdx}-${tIdx}`}
                        className={`text-xs ${
                          skillsMode === 'bubble'
                            ? 'px-3 py-0.5 rounded-full border border-[var(--color-accent)]/30 bg-[var(--color-accent)]/5 text-[var(--color-text)]'
                            : 'px-2 py-0.5 rounded border border-[var(--color-divider)] bg-[var(--color-sidebar-background)] text-[var(--color-text)]'
                        }`}
                        style={{ fontSize: 'var(--font-size-body)' }}
                      >
                        {renderInlineMarkup(tag.trim())}
                        {bullet.proficiency ? renderProficiency(bullet.proficiency) : null}
                      </span>
                    ));
                  })}
                </div>
              )}

              {/* Paragraph Variant */}
              {isParagraph && item.bullets && item.bullets.length > 0 && (
                <div
                  className="mt-1 leading-relaxed text-[var(--color-text)]"
                  style={{ fontSize: 'var(--font-size-body)' }}
                >
                  {item.bullets.map((b) => (
                    <React.Fragment key={b.id}>
                      {renderInlineMarkup(b.text)}
                    </React.Fragment>
                  ))}
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
                          {bullet.proficiency ? renderProficiency(bullet.proficiency) : null}
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
      )}
    </section>
  );
};

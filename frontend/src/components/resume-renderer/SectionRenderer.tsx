import React from 'react';
import { ResumeSection, SectionItem, BulletItem } from '@/types/content';
import { HeadingStyle, BulletStyle } from '@/types/style';

interface SectionRendererProps {
  section: ResumeSection;
  headingStyle: HeadingStyle;
  bulletStyle: BulletStyle;
}

export const SectionRenderer: React.FC<SectionRendererProps> = ({
  section,
  headingStyle,
  bulletStyle,
}) => {
  if (!section.visible || (!section.items || section.items.length === 0)) {
    return null;
  }

  // Heading style decoration
  const getHeadingClasses = () => {
    switch (headingStyle) {
      case 'underline':
        return 'border-b-2 border-[var(--color-accent)] pb-1 mb-2 font-bold';
      case 'bar':
        return 'border-l-4 border-[var(--color-accent)] pl-2 mb-2 font-bold';
      case 'caps':
        return 'uppercase tracking-wider border-b border-[var(--color-divider)] pb-1 mb-2 font-semibold text-[var(--color-accent)]';
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
      case 'none':
      default:
        return null;
    }
  };

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
        {section.items.map((item, itemIdx) => (
          <div
            key={item.id || itemIdx}
            className="resume-item"
            style={{
              marginBottom:
                itemIdx === section.items.length - 1
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
                      {item.title}
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
                      {item.subtitle}
                    </span>
                  )}
                </div>

                {/* Right aligned Meta: Date & Location */}
                <div
                  className="text-right text-[var(--color-muted)] whitespace-nowrap ml-auto"
                  style={{ fontSize: 'var(--font-size-meta)' }}
                >
                  {item.dateRange && <span>{item.dateRange}</span>}
                  {item.dateRange && item.location && <span>, </span>}
                  {item.location && <span>{item.location}</span>}
                </div>
              </div>
            )}

            {/* Bullets */}
            {item.bullets && item.bullets.length > 0 && (
              <div className="mt-1 flex flex-col">
                {item.bullets.map((bullet, bIdx) => (
                  <div
                    key={bullet.id || bIdx}
                    className="flex items-start leading-snug"
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
                      {bullet.text}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
};

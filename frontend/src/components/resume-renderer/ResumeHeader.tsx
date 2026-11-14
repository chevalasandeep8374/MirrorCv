import React from 'react';
import { HeaderContent } from '@/types/content';

interface ResumeHeaderProps {
  header: HeaderContent;
}

export const ResumeHeader: React.FC<ResumeHeaderProps> = ({ header }) => {
  const contactItems: { label: string; value: string; isLink?: boolean; href?: string }[] = [];

  if (header.email) contactItems.push({ label: 'Email', value: header.email, isLink: true, href: `mailto:${header.email}` });
  if (header.phone) contactItems.push({ label: 'Phone', value: header.phone, isLink: true, href: `tel:${header.phone}` });
  if (header.location) contactItems.push({ label: 'Location', value: header.location });
  if (header.website) contactItems.push({ label: 'Website', value: header.website.replace(/^https?:\/\//, ''), isLink: true, href: header.website });

  header.links?.forEach((link) => {
    if (link.label && link.url) {
      contactItems.push({ label: link.label, value: link.label, isLink: true, href: link.url });
    }
  });

  return (
    <header
      className="pb-[var(--spacing-header-bottom)] mb-[var(--spacing-header-bottom)] border-b border-[var(--color-divider)]"
      style={{
        marginBottom: 'var(--spacing-header-bottom)',
      }}
    >
      {header.name && (
        <h1
          className="font-[family-name:var(--font-heading)] font-extrabold tracking-tight text-[var(--color-text)] leading-tight"
          style={{ fontSize: 'var(--font-size-name)' }}
        >
          {header.name}
        </h1>
      )}

      {header.title && (
        <p
          className="font-medium text-[var(--color-accent)] mt-1 tracking-wide"
          style={{ fontSize: 'var(--font-size-header-title)' }}
        >
          {header.title}
        </p>
      )}

      {contactItems.length > 0 && (
        <div
          className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 text-[var(--color-muted)]"
          style={{ fontSize: 'var(--font-size-contact)' }}
        >
          {contactItems.map((item, idx) => (
            <React.Fragment key={idx}>
              {idx > 0 && <span className="text-[var(--color-divider)] select-none">•</span>}
              {item.isLink && item.href ? (
                <a
                  href={item.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline hover:text-[var(--color-accent)] transition-colors"
                >
                  {item.value}
                </a>
              ) : (
                <span>{item.value}</span>
              )}
            </React.Fragment>
          ))}
        </div>
      )}
    </header>
  );
};

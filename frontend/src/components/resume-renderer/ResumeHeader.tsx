import React from 'react';
import { HeaderContent } from '@/types/content';
import { Decorations } from '@/types/style';

interface ResumeHeaderProps {
  header: HeaderContent;
  decorations?: Decorations;
  isBanner?: boolean;
}

export const ResumeHeader: React.FC<ResumeHeaderProps> = ({
  header,
  decorations,
  isBanner = false,
}) => {
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

  const showAvatar = decorations?.showAvatar ?? Boolean(header.photoUrl || decorations?.avatarUrl);
  const avatarSrc = header.photoUrl || decorations?.avatarUrl;
  const avatarShape = decorations?.avatarShape || 'circle';

  if (isBanner) {
    const bannerBg = decorations?.headerBannerColor || 'var(--color-header-banner, #0f172a)';
    const bannerText = decorations?.headerBannerTextColor || 'var(--color-header-banner-text, #ffffff)';

    return (
      <header
        className="rounded-lg p-5 mb-[var(--spacing-header-bottom)] flex items-center justify-between gap-5 transition-colors shadow-sm"
        style={{
          backgroundColor: bannerBg,
          color: bannerText,
          marginBottom: 'var(--spacing-header-bottom)',
        }}
      >
        <div className="flex-1 min-w-0">
          {header.name && (
            <h1
              className="font-[family-name:var(--font-heading)] font-extrabold tracking-tight leading-tight"
              style={{ fontSize: 'var(--font-size-name)', color: bannerText }}
            >
              {header.name}
            </h1>
          )}

          {header.title && (
            <p
              className="font-medium mt-1 tracking-wide opacity-90"
              style={{ fontSize: 'var(--font-size-header-title)', color: bannerText }}
            >
              {header.title}
            </p>
          )}

          {contactItems.length > 0 && (
            <div
              className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2.5 opacity-85"
              style={{ fontSize: 'var(--font-size-contact)' }}
            >
              {contactItems.map((item, idx) => (
                <React.Fragment key={idx}>
                  {idx > 0 && <span className="opacity-40 select-none">•</span>}
                  {item.isLink && item.href ? (
                    <a
                      href={item.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:underline hover:opacity-100 transition-opacity"
                      style={{ color: bannerText }}
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
        </div>

        {showAvatar && avatarSrc && (
          <div className="shrink-0">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={avatarSrc}
              alt={header.name || 'Profile photo'}
              className={`w-20 h-20 object-cover border-2 border-white/30 shadow-md ${
                avatarShape === 'circle' ? 'rounded-full' : 'rounded-lg'
              }`}
            />
          </div>
        )}
      </header>
    );
  }

  return (
    <header
      className="pb-[var(--spacing-header-bottom)] mb-[var(--spacing-header-bottom)] border-b border-[var(--color-divider)] flex items-start justify-between gap-4"
      style={{
        marginBottom: 'var(--spacing-header-bottom)',
      }}
    >
      <div className="flex-1 min-w-0">
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
      </div>

      {showAvatar && avatarSrc && (
        <div className="shrink-0 ml-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={avatarSrc}
            alt={header.name || 'Profile photo'}
            className={`w-18 h-18 object-cover border border-[var(--color-divider)] shadow-sm ${
              avatarShape === 'circle' ? 'rounded-full' : 'rounded-md'
            }`}
          />
        </div>
      )}
    </header>
  );
};

import React from 'react';
import { HeaderContent } from '@/types/content';
import { Decorations, HeaderConfig, PhotoConfig } from '@/types/style';

interface ResumeHeaderProps {
  header: HeaderContent;
  decorations?: Decorations;
  headerConfig?: HeaderConfig;
  photoConfig?: PhotoConfig;
  isBanner?: boolean;
}

export const ResumeHeader: React.FC<ResumeHeaderProps> = ({
  header,
  decorations,
  headerConfig,
  photoConfig,
  isBanner = false,
}) => {
  const fieldVis = header.fieldVisibility || {
    name: true,
    title: true,
    email: true,
    phone: true,
    location: true,
    website: true,
    photo: true,
  };

  const contactItems: { label: string; value: string; isLink?: boolean; href?: string }[] = [];

  if (fieldVis.email !== false && header.email) {
    contactItems.push({ label: 'Email', value: header.email, isLink: true, href: `mailto:${header.email}` });
  }
  if (fieldVis.phone !== false && header.phone) {
    contactItems.push({ label: 'Phone', value: header.phone, isLink: true, href: `tel:${header.phone}` });
  }
  if (fieldVis.location !== false && header.location) {
    contactItems.push({ label: 'Location', value: header.location });
  }
  if (fieldVis.website !== false && header.website) {
    const rawWeb = header.website.trim();
    const lowerWeb = rawWeb.toLowerCase();
    const isDangerous = lowerWeb.startsWith('javascript:') || lowerWeb.startsWith('data:') || lowerWeb.startsWith('vbscript:');
    if (!isDangerous) {
      contactItems.push({
        label: 'Website',
        value: rawWeb.replace(/^https?:\/\//, ''),
        isLink: true,
        href: rawWeb.startsWith('http') ? rawWeb : `https://${rawWeb}`,
      });
    }
  }

  header.links?.forEach((link) => {
    if (link.label && link.url) {
      const rawUrl = link.url.trim();
      const lowerUrl = rawUrl.toLowerCase();
      const isDangerous = lowerUrl.startsWith('javascript:') || lowerUrl.startsWith('data:') || lowerUrl.startsWith('vbscript:');
      if (!isDangerous) {
        contactItems.push({
          label: link.label,
          value: link.label,
          isLink: true,
          href: rawUrl.startsWith('http') ? rawUrl : `https://${rawUrl}`,
        });
      }
    }
  });

  const showAvatar =
    fieldVis.photo !== false &&
    (decorations?.showAvatar ?? Boolean(header.photoUrl || decorations?.avatarUrl));
  const avatarSrc = header.photoUrl || decorations?.avatarUrl;

  // Photo shape, size, border, position
  const shape = photoConfig?.shape || decorations?.avatarShape || 'circle';
  const shapeClass =
    shape === 'circle' ? 'rounded-full' : shape === 'rounded' ? 'rounded-xl' : 'rounded-md';

  const size = photoConfig?.size || 'medium';
  const sizeClass =
    size === 'small' ? 'w-16 h-16' : size === 'large' ? 'w-24 h-24' : 'w-20 h-20';

  const border = photoConfig?.border || 'thin';
  const borderClass =
    border === 'none'
      ? 'border-0'
      : border === 'thick'
      ? 'border-2 border-[var(--color-divider)]'
      : border === 'accent'
      ? 'border-2 border-[var(--color-accent)]'
      : 'border border-[var(--color-divider)]';

  // Header alignment and separator
  const isCentered = headerConfig?.alignment === 'center';
  const arrangement = headerConfig?.arrangement || 'bullet';
  const separatorChar =
    arrangement === 'pipe' ? '|' : arrangement === 'bar' ? '/' : '•';

  if (isBanner) {
    const bannerBg = decorations?.headerBannerColor || 'var(--color-header-banner, #0f172a)';
    const bannerText = decorations?.headerBannerTextColor || 'var(--color-header-banner-text, #ffffff)';

    return (
      <header
        className={`rounded-lg p-5 mb-[var(--spacing-header-bottom)] flex items-center justify-between gap-5 transition-colors shadow-sm ${
          isCentered ? 'text-center flex-col justify-center' : ''
        }`}
        style={{
          backgroundColor: bannerBg,
          color: bannerText,
          marginBottom: 'var(--spacing-header-bottom)',
        }}
      >
        <div className={`flex-1 min-w-0 ${isCentered ? 'flex flex-col items-center' : ''}`}>
          {fieldVis.name !== false && header.name && (
            <h1
              className="font-[family-name:var(--font-heading)] font-extrabold tracking-tight leading-tight"
              style={{ fontSize: 'var(--font-size-name)', color: bannerText }}
            >
              {header.name}
            </h1>
          )}

          {fieldVis.title !== false && header.title && (
            <p
              className="font-medium mt-1 tracking-wide opacity-90"
              style={{ fontSize: 'var(--font-size-header-title)', color: bannerText }}
            >
              {header.title}
            </p>
          )}

          {contactItems.length > 0 && (
            <div
              className={`flex flex-wrap items-center gap-x-3 gap-y-1 mt-2.5 opacity-85 ${
                isCentered ? 'justify-center' : ''
              }`}
              style={{ fontSize: 'var(--font-size-contact)' }}
            >
              {contactItems.map((item, idx) => (
                <React.Fragment key={idx}>
                  {idx > 0 && <span className="opacity-40 select-none">{separatorChar}</span>}
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
              className={`${sizeClass} object-cover border-2 border-white/30 shadow-md ${shapeClass}`}
            />
          </div>
        )}
      </header>
    );
  }

  return (
    <header
      className={`pb-[var(--spacing-header-bottom)] mb-[var(--spacing-header-bottom)] border-b border-[var(--color-divider)] flex items-start justify-between gap-4 ${
        isCentered ? 'text-center flex-col items-center justify-center' : ''
      }`}
      style={{
        marginBottom: 'var(--spacing-header-bottom)',
      }}
    >
      <div className={`flex-1 min-w-0 ${isCentered ? 'flex flex-col items-center' : ''}`}>
        {fieldVis.name !== false && header.name && (
          <h1
            className="font-[family-name:var(--font-heading)] font-extrabold tracking-tight text-[var(--color-text)] leading-tight"
            style={{
              fontSize: 'var(--font-size-name)',
              color: 'var(--accent-name, var(--color-text))',
            }}
          >
            {header.name}
          </h1>
        )}

        {fieldVis.title !== false && header.title && (
          <p
            className="font-medium mt-1 tracking-wide"
            style={{
              fontSize: 'var(--font-size-header-title)',
              color: 'var(--accent-job-title, var(--color-accent))',
            }}
          >
            {header.title}
          </p>
        )}

        {contactItems.length > 0 && (
          <div
            className={`flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 text-[var(--color-muted)] ${
              isCentered ? 'justify-center' : ''
            }`}
            style={{ fontSize: 'var(--font-size-contact)' }}
          >
            {contactItems.map((item, idx) => (
              <React.Fragment key={idx}>
                {idx > 0 && <span className="text-[var(--color-divider)] select-none">{separatorChar}</span>}
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
        <div className={`shrink-0 ${isCentered ? 'mt-2' : 'ml-3'}`}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={avatarSrc}
            alt={header.name || 'Profile photo'}
            className={`${sizeClass} object-cover shadow-sm ${borderClass} ${shapeClass}`}
          />
        </div>
      )}
    </header>
  );
};

import React from 'react';
import { FooterConfig } from '@/types/style';
import { HeaderContent } from '@/types/content';

interface PageFooterProps {
  footer?: FooterConfig;
  header: HeaderContent;
  pageNumber: number;
  totalPages: number;
}

export const PageFooter: React.FC<PageFooterProps> = ({
  footer,
  header,
  pageNumber,
  totalPages,
}) => {
  if (!footer) return null;

  const showPageNumbers = footer.showPageNumbers ?? true;
  const showEmail = footer.showEmail ?? false;
  const showName = footer.showName ?? false;

  if (!showPageNumbers && !showEmail && !showName) {
    return null;
  }

  return (
    <footer className="mt-auto pt-3 border-t border-[var(--color-divider)] flex justify-between items-center text-[10px] text-[var(--color-muted)] font-sans select-none">
      <div className="flex items-center gap-2">
        {showName && header.name && <span className="font-medium">{header.name}</span>}
        {showName && showEmail && header.email && <span>•</span>}
        {showEmail && header.email && <span>{header.email}</span>}
      </div>

      <div>
        {showPageNumbers && (
          <span>
            {pageNumber} / {totalPages}
          </span>
        )}
      </div>
    </footer>
  );
};

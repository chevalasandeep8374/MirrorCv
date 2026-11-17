import React from 'react';
import { PageSize } from '@/types/style';

interface PageViewProps {
  pageSize: PageSize;
  pageNumber: number;
  totalPages: number;
  children: React.ReactNode;
  isPrint?: boolean;
}

export const PageView: React.FC<PageViewProps> = ({
  pageSize,
  pageNumber,
  totalPages,
  children,
  isPrint = false,
}) => {
  const isA4 = pageSize === 'A4';

  return (
    <div
      className={`relative bg-[var(--color-background)] text-[var(--color-text)] font-[family-name:var(--font-base)] leading-[var(--line-height)] mx-auto overflow-hidden transition-shadow select-text ${
        isPrint
          ? 'print-page shadow-none'
          : 'shadow-2xl rounded-sm mb-8 ring-1 ring-black/5'
      }`}
      style={{
        width: isA4 ? '210mm' : '8.5in',
        minHeight: isA4 ? '297mm' : '11in',
        height: isA4 ? '297mm' : '11in',
        boxSizing: 'border-box',
        pageBreakAfter: pageNumber === totalPages ? 'auto' : 'always',
        breakAfter: pageNumber === totalPages ? 'auto' : 'page',
      }}
    >
      {/* Printable Area with tokens margins */}
      <div
        className="w-full h-full flex flex-col box-border"
        style={{
          paddingTop: 'var(--margin-top)',
          paddingBottom: 'var(--margin-bottom)',
          paddingLeft: 'var(--margin-left)',
          paddingRight: 'var(--margin-right)',
        }}
      >
        {children}
      </div>

      {/* On-screen Page Badge (hidden during print) */}
      {!isPrint && (
        <div className="absolute bottom-2 right-4 text-[10px] text-gray-400 font-sans tracking-wide uppercase select-none pointer-events-none print:hidden">
          Page {pageNumber} of {totalPages}
        </div>
      )}
    </div>
  );
};

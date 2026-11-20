'use client';

import React, { useRef, useEffect, useMemo } from 'react';
import { useResume } from '@/context/ResumeContext';
import { ResumeDocument } from '@/components/resume-renderer/ResumeDocument';
import { paginateResume } from '@/lib/pagination';
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  RotateCcw,
  Scissors,
  FileText,
  Sparkles,
} from 'lucide-react';

export const LivePreviewPane: React.FC = () => {
  const {
    content,
    style,
    zoom,
    setZoom,
    activeTab,
    onePageFitActive,
    onePageFitWarning,
    toggleOnePageFit,
  } = useResume();

  const containerRef = useRef<HTMLDivElement>(null);
  const pages = useMemo(() => paginateResume(content, style), [content, style]);
  const totalPages = pages.length;

  const handleFitToWidth = () => {
    if (!containerRef.current) return;
    const containerWidth = containerRef.current.clientWidth;
    // Standard A4 width is 794px at 96 DPI, Letter is ~816px.
    const docWidth = style.pageSize === 'Letter' ? 816 : 794;
    const availableWidth = Math.max(300, containerWidth - 64);
    const calculatedScale = Math.min(1.5, Math.max(0.4, availableWidth / docWidth));
    setZoom(Number(calculatedScale.toFixed(2)));
  };

  const handleZoomIn = () => {
    setZoom((prev) => Math.min(2.0, Number((prev + 0.1).toFixed(2))));
  };

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(0.4, Number((prev - 0.1).toFixed(2))));
  };

  const handleResetZoom = () => {
    setZoom(1.0);
  };

  return (
    <div
      ref={containerRef}
      className="flex-1 bg-[#ECEEF2] overflow-auto custom-scrollbar scroll-smooth p-6 sm:p-8 flex flex-col items-center justify-start min-h-full relative select-none"
    >
      {/* Center Glassmorphic Indicator for AI Mode */}
      {activeTab === 'ai' && (
        <div className="sticky top-2 z-40 mb-3 pointer-events-none">
          <div className="pointer-events-auto inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/95 border border-pink-200 shadow-md text-slate-900 text-xs font-semibold animate-dropdown-fade">
            <span className="w-2 h-2 rounded-full bg-[#FF2D6C] animate-pulse" />
            <span className="text-[#FF2D6C] font-semibold">AI Diff Mode: 3 Optimizations Highlighted</span>
          </div>
        </div>
      )}

      {/* Floating Preview Controls Toolbar (Glassmorphic Centered Capsule) */}
      <div className="sticky top-4 z-30 mb-6 bg-white/95 backdrop-blur-md border border-slate-200/90 shadow-md hover:shadow-lg rounded-full px-3.5 py-1.5 flex items-center gap-2.5 text-xs text-slate-800 transition-all duration-200">
        {/* Zoom Controls: [-] 100% [+] */}
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={handleZoomOut}
            aria-label="Zoom out"
            className="w-6 h-6 rounded-full hover:bg-slate-100 flex items-center justify-center text-slate-500 hover:text-slate-900 transition-colors cursor-pointer"
            title="Zoom out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="font-mono text-xs font-semibold text-slate-900 px-1 min-w-[44px] text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            type="button"
            onClick={handleZoomIn}
            aria-label="Zoom in"
            className="w-6 h-6 rounded-full hover:bg-slate-100 flex items-center justify-center text-slate-500 hover:text-slate-900 transition-colors cursor-pointer"
            title="Zoom in"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="h-3.5 border-r border-slate-200" />

        {/* Fit Width button */}
        <button
          type="button"
          onClick={handleFitToWidth}
          className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors cursor-pointer"
          title="Fit document to available window width"
        >
          <Maximize2 className="w-3.5 h-3.5" />
          <span>Fit Width</span>
        </button>

        {/* 1-Page Fit Auto-Scale Toggle Pill */}
        <button
          type="button"
          onClick={toggleOnePageFit}
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium transition-colors cursor-pointer ${
            onePageFitActive
              ? 'bg-emerald-600 text-white shadow-xs'
              : 'bg-emerald-50 text-emerald-800 border border-emerald-300 hover:bg-emerald-100'
          }`}
          title="Intelligently compress typography & spacing to fit onto exactly 1 page"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>1-Page Fit</span>
        </button>

        <div className="h-3.5 border-r border-slate-200" />

        {/* Page Format & Count Indicator */}
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded text-slate-500 font-mono text-[11px] font-medium">
          <span className="px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-800 font-bold text-xs tracking-wider">
            {style.pageSize || 'A4'}
          </span>
          <span>{totalPages > 1 ? `${totalPages} Pages` : '1 Page'}</span>
        </div>
      </div>

      {/* Rendered Scaled Document Container */}
      <div
        className="transition-transform duration-150 origin-top flex flex-col items-center"
        style={{
          transform: `scale(${zoom})`,
          marginBottom: '100px',
        }}
      >
        <ResumeDocument content={content} style={style} />
      </div>
    </div>
  );
};

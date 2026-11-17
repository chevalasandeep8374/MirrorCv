'use client';

import React, { useRef, useEffect } from 'react';
import { useResume } from '@/context/ResumeContext';
import { ResumeDocument } from '@/components/resume-renderer/ResumeDocument';
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
    onePageFitActive,
    onePageFitWarning,
    toggleOnePageFit,
  } = useResume();

  const containerRef = useRef<HTMLDivElement>(null);

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
      className="flex-1 bg-slate-200/70 overflow-auto p-8 flex flex-col items-center justify-start min-h-full relative select-none"
    >
      {/* Floating Preview Controls Toolbar (Glass-1) */}
      <div className="sticky top-4 z-30 mb-6 glass-1 border border-border-subtle rounded-full shadow-card px-4 py-1.5 flex items-center gap-2 text-xs">
        {/* Zoom Out */}
        <button
          type="button"
          onClick={handleZoomOut}
          className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-full transition-colors"
          title="Zoom out"
        >
          <ZoomOut className="w-3.5 h-3.5" />
        </button>

        {/* Zoom Percent Display */}
        <span className="font-mono font-bold text-[11px] text-slate-700 w-12 text-center">
          {Math.round(zoom * 100)}%
        </span>

        {/* Zoom In */}
        <button
          type="button"
          onClick={handleZoomIn}
          className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-full transition-colors"
          title="Zoom in"
        >
          <ZoomIn className="w-3.5 h-3.5" />
        </button>

        <div className="h-4 w-px bg-slate-200 mx-1" />

        {/* Fit to Width */}
        <button
          type="button"
          onClick={handleFitToWidth}
          className="px-2.5 py-1 text-slate-700 hover:text-primary hover:bg-blue-50 rounded-full font-bold text-[11px] transition-colors flex items-center gap-1"
          title="Fit document to available window width"
        >
          <Maximize2 className="w-3 h-3" />
          <span>Fit Width</span>
        </button>

        {/* Reset 100% */}
        <button
          type="button"
          onClick={handleResetZoom}
          className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors"
          title="Reset to 100%"
        >
          <RotateCcw className="w-3 h-3" />
        </button>

        <div className="h-4 w-px bg-slate-200 mx-1" />

        {/* One-Page Fit Toggle Pill */}
        <button
          type="button"
          onClick={toggleOnePageFit}
          className={`px-2.5 py-1 rounded-xl font-bold text-[11px] transition-all flex items-center gap-1 ${
            onePageFitActive
              ? 'bg-blue-600 text-white shadow-xs'
              : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
          }`}
          title="Intelligently compress typography & spacing to fit onto exactly 1 page"
        >
          <Sparkles className="w-3 h-3" />
          <span>{onePageFitActive ? '1-Page Fit Active' : '1-Page Fit'}</span>
        </button>

        {/* Page Size Badge */}
        <span className="text-[10px] font-mono font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-lg ml-1">
          {style.pageSize || 'A4'}
        </span>
      </div>

      {/* Rendered Scaled Document Container */}
      <div
        className="transition-transform duration-150 origin-top flex flex-col items-center shadow-2xl rounded-sm"
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

'use client';

import React, { useState, useRef, useCallback } from 'react';
import { Sliders, Eye, Sparkles } from 'lucide-react';

interface PdfCompareSliderProps {
  originalPdfUrl: string;
  tailoredPdfUrl: string;
}

export default function PdfCompareSlider({
  originalPdfUrl,
  tailoredPdfUrl,
}: PdfCompareSliderProps) {
  const [sliderPos, setSliderPos] = useState<number>(50); // percentage 0 to 100
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handlePointerDown = () => {
    setIsDragging(true);
  };

  const handlePointerUp = () => {
    setIsDragging(false);
  };

  const handlePointerMove = useCallback(
    (e: React.PointerEvent<HTMLDivElement>) => {
      if (!isDragging || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
      setSliderPos(percentage);
    },
    [isDragging]
  );

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-slate-900 select-none">
      {/* Top Slider Controls Bar */}
      <div className="h-10 bg-slate-800 border-b border-slate-700 px-6 flex items-center justify-between text-xs text-slate-300 flex-shrink-0">
        <div className="flex items-center space-x-3">
          <Sliders className="w-4 h-4 text-blue-400" />
          <span className="font-bold text-white tracking-wide">
            Overlay Compare Slider
          </span>
          <span className="text-[11px] text-slate-400">
            Drag divider left/right to inspect pixel-perfect text & layout alignment
          </span>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="text-[11px] font-semibold text-slate-400">Split:</span>
            <input
              type="range"
              min="0"
              max="100"
              value={sliderPos}
              onChange={(e) => setSliderPos(Number(e.target.value))}
              className="w-32 h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
            <span className="w-8 font-mono text-[11px] text-blue-400 font-bold">
              {Math.round(sliderPos)}%
            </span>
          </div>

          <button
            onClick={() => setSliderPos(50)}
            className="px-2 py-0.5 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 text-[11px] font-medium transition"
          >
            Reset 50%
          </button>
        </div>
      </div>

      {/* Main Slider Canvas */}
      <div
        ref={containerRef}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
        className="relative flex-1 w-full h-full overflow-hidden cursor-ew-resize bg-slate-950 flex items-center justify-center"
      >
        {/* Layer 1: Tailored PDF (Full Background Layer) */}
        <div className="absolute inset-0 w-full h-full">
          <iframe
            src={tailoredPdfUrl}
            className={`w-full h-full border-none ${isDragging ? 'pointer-events-none' : ''}`}
            title="Tailored PDF Overlay"
          />
          <div className="absolute top-4 right-6 pointer-events-none z-10 px-2.5 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 font-bold text-xs shadow-lg backdrop-blur-md flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            <span>Tailored Output</span>
          </div>
        </div>

        {/* Layer 2: Original PDF (Clipped Left Layer) */}
        <div
          className="absolute inset-0 h-full overflow-hidden border-r border-blue-400 shadow-[4px_0_24px_rgba(0,0,0,0.5)]"
          style={{ width: `${sliderPos}%` }}
        >
          <div
            className="h-full"
            style={{
              width: containerRef.current ? `${containerRef.current.clientWidth}px` : '100vw',
            }}
          >
            <iframe
              src={originalPdfUrl}
              className={`w-full h-full border-none ${isDragging ? 'pointer-events-none' : ''}`}
              title="Original PDF Overlay"
            />
          </div>

          <div className="absolute top-4 left-6 pointer-events-none z-10 px-2.5 py-1 rounded-full bg-slate-900/80 border border-slate-600 text-slate-200 font-bold text-xs shadow-lg backdrop-blur-md flex items-center gap-1.5">
            <Eye className="w-3.5 h-3.5 text-slate-400" />
            <span>Original Template</span>
          </div>
        </div>

        {/* Vertical Divider Drag Handle */}
        <div
          onPointerDown={handlePointerDown}
          className="absolute top-0 bottom-0 z-30 flex items-center justify-center cursor-ew-resize"
          style={{ left: `calc(${sliderPos}% - 14px)` }}
        >
          <div className="w-7 h-12 rounded-full bg-blue-600 text-white shadow-xl flex items-center justify-center border-2 border-white hover:scale-110 active:scale-95 transition-transform">
            <Sliders className="w-3.5 h-3.5 rotate-90" />
          </div>
        </div>
      </div>
    </div>
  );
}

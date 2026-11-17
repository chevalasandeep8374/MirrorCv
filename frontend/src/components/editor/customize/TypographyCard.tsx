'use client';

import React from 'react';
import { useResume } from '@/context/ResumeContext';
import { Type, Sliders, RotateCcw } from 'lucide-react';
import { FontSizeOffsets } from '@/types/style';

export const TypographyCard: React.FC = () => {
  const { style, updateStyle, startStyleDrag, endStyleDrag } = useResume();

  const typography = style.typography;
  const baseFontSize = typography.baseFontSize ?? 9.5;
  const offsets = typography.fontSizeOffsets || {
    name: 12.5,
    headerTitle: 1.5,
    contact: -0.5,
    sectionHeading: 3.0,
    itemTitle: 1.0,
    itemSubtitle: 0.0,
    body: 0.0,
    meta: -1.0,
  };
  const lineHeight = typography.lineHeight ?? 1.45;

  const handleBaseSizeChange = (val: number) => {
    updateStyle({
      ...style,
      typography: {
        ...style.typography,
        baseFontSize: val,
        fontSizeOffsets: offsets,
        fontSizeScale: 1.0,
      },
    });
  };

  const handleOffsetChange = (role: keyof FontSizeOffsets, val: number) => {
    updateStyle({
      ...style,
      typography: {
        ...style.typography,
        fontSizeOffsets: {
          ...offsets,
          [role]: val,
        },
      },
    });
  };

  const handleLineHeightChange = (val: number) => {
    updateStyle({
      ...style,
      typography: {
        ...style.typography,
        lineHeight: val,
      },
    });
  };

  const handleResetDefaults = () => {
    updateStyle({
      ...style,
      typography: {
        ...style.typography,
        baseFontSize: 9.5,
        fontSizeOffsets: {
          name: 12.5,
          headerTitle: 1.5,
          contact: -0.5,
          sectionHeading: 3.0,
          itemTitle: 1.0,
          itemSubtitle: 0.0,
          body: 0.0,
          meta: -1.0,
        },
        lineHeight: 1.45,
        fontSizeScale: 1.0,
      },
    });
  };

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-5">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-purple-50 text-purple-600 rounded-xl">
            <Type className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-slate-900">Typography & Sizes</h3>
            <p className="text-xs text-slate-500">Base document size and role-specific offsets (pt)</p>
          </div>
        </div>
        <button
          type="button"
          onClick={handleResetDefaults}
          title="Reset typography to defaults"
          className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* 1. Base Font Size */}
      <div className="p-3.5 bg-purple-50/50 rounded-xl border border-purple-100 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="font-bold text-purple-900 flex items-center gap-1.5">
            <Sliders className="w-3.5 h-3.5 text-purple-600" /> Base Font Size (pt)
          </span>
          <span className="font-mono font-bold text-purple-700 bg-white px-2 py-0.5 rounded border border-purple-200">
            {baseFontSize.toFixed(2)} pt
          </span>
        </div>
        <input
          type="range"
          aria-label="Base Font Size"
          min={8.0}
          max={12.0}
          step={0.25}
          value={baseFontSize}
          onPointerDown={startStyleDrag}
          onPointerUp={endStyleDrag}
          onChange={(e) => handleBaseSizeChange(Number(e.target.value))}
          className="w-full h-1.5 bg-purple-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
        />
        <div className="flex justify-between text-[10px] text-purple-400 font-mono">
          <span>8.0 pt (Compact)</span>
          <span>9.5 pt (Standard)</span>
          <span>12.0 pt (Large)</span>
        </div>
      </div>

      {/* 2. Relative Offsets */}
      <div className="space-y-3">
        <label className="text-xs font-semibold text-slate-700">Role-Specific Font Offsets</label>
        
        {/* Name */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-600">Candidate Name</span>
            <div className="flex items-center gap-1.5 text-xs font-mono">
              <span className="text-slate-400 text-[10px]">
                ({(baseFontSize + (offsets.name ?? 12.5)).toFixed(1)} pt)
              </span>
              <span className="font-bold text-purple-700">
                +{(offsets.name ?? 12.5).toFixed(1)} pt
              </span>
            </div>
          </div>
          <input
            type="range"
            aria-label="Candidate Name Font Offset"
            min={8.0}
            max={18.0}
            step={0.5}
            value={offsets.name ?? 12.5}
            onChange={(e) => handleOffsetChange('name', Number(e.target.value))}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
          />
        </div>

        {/* Section Heading */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-600">Section Headings</span>
            <div className="flex items-center gap-1.5 text-xs font-mono">
              <span className="text-slate-400 text-[10px]">
                ({(baseFontSize + (offsets.sectionHeading ?? 3.0)).toFixed(1)} pt)
              </span>
              <span className="font-bold text-purple-700">
                +{(offsets.sectionHeading ?? 3.0).toFixed(1)} pt
              </span>
            </div>
          </div>
          <input
            type="range"
            aria-label="Section Heading Font Offset"
            min={1.0}
            max={6.0}
            step={0.5}
            value={offsets.sectionHeading ?? 3.0}
            onChange={(e) => handleOffsetChange('sectionHeading', Number(e.target.value))}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
          />
        </div>

        {/* Entry Title */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-600">Entry Title (Role / Degree)</span>
            <div className="flex items-center gap-1.5 text-xs font-mono">
              <span className="text-slate-400 text-[10px]">
                ({(baseFontSize + (offsets.itemTitle ?? 1.0)).toFixed(1)} pt)
              </span>
              <span className="font-bold text-purple-700">
                +{(offsets.itemTitle ?? 1.0).toFixed(1)} pt
              </span>
            </div>
          </div>
          <input
            type="range"
            aria-label="Entry Title Font Offset"
            min={0.0}
            max={4.0}
            step={0.5}
            value={offsets.itemTitle ?? 1.0}
            onChange={(e) => handleOffsetChange('itemTitle', Number(e.target.value))}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
          />
        </div>

        {/* Meta / Dates */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-600">Meta (Dates & Location)</span>
            <div className="flex items-center gap-1.5 text-xs font-mono">
              <span className="text-slate-400 text-[10px]">
                ({(baseFontSize + (offsets.meta ?? -1.0)).toFixed(1)} pt)
              </span>
              <span className="font-bold text-purple-700">
                {(offsets.meta ?? -1.0).toFixed(1)} pt
              </span>
            </div>
          </div>
          <input
            type="range"
            aria-label="Meta Font Offset"
            min={-3.0}
            max={1.0}
            step={0.5}
            value={offsets.meta ?? -1.0}
            onChange={(e) => handleOffsetChange('meta', Number(e.target.value))}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
          />
        </div>
      </div>

      {/* 3. Line Height Slider */}
      <div className="space-y-2 pt-2 border-t border-slate-100">
        <div className="flex items-center justify-between text-xs">
          <span className="font-semibold text-slate-700">Line Height Multiplier</span>
          <span className="font-mono font-bold text-purple-600 bg-slate-50 px-2 py-0.5 rounded border border-slate-200">
            {lineHeight.toFixed(2)}×
          </span>
        </div>
        <input
          type="range"
          aria-label="Line Height Multiplier"
          min={1.2}
          max={1.75}
          step={0.05}
          value={lineHeight}
          onChange={(e) => handleLineHeightChange(Number(e.target.value))}
          className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
        />
        <div className="flex justify-between text-[10px] text-slate-400 font-mono">
          <span>1.20× (Tight)</span>
          <span>1.45× (Standard)</span>
          <span>1.75× (Spacious)</span>
        </div>
      </div>
    </div>
  );
};

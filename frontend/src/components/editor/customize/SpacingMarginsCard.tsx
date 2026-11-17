'use client';

import React from 'react';
import { useResume } from '@/context/ResumeContext';
import { Move, Sliders } from 'lucide-react';

const MM_TO_PT = 2.83465;
const PT_TO_MM = 1 / MM_TO_PT;

export const SpacingMarginsCard: React.FC = () => {
  const { style, updateStyle } = useResume();

  const margins = style.margins;
  const spacing = style.spacing;

  // Convert stored pt to mm for UI display
  const topMm = Math.round((margins.top || 36) * PT_TO_MM);
  const bottomMm = Math.round((margins.bottom || 36) * PT_TO_MM);
  const leftMm = Math.round((margins.left || 40) * PT_TO_MM);
  const rightMm = Math.round((margins.right || 40) * PT_TO_MM);

  const handleMarginChange = (side: 'topBottom' | 'leftRight', valMm: number) => {
    const valPt = Math.round(valMm * MM_TO_PT);
    if (side === 'topBottom') {
      updateStyle({
        ...style,
        margins: {
          ...style.margins,
          top: valPt,
          bottom: valPt,
          unit: 'pt',
        },
      });
    } else {
      updateStyle({
        ...style,
        margins: {
          ...style.margins,
          left: valPt,
          right: valPt,
          unit: 'pt',
        },
      });
    }
  };

  const handleApplyMarginPreset = (presetMm: number) => {
    const valPt = Math.round(presetMm * MM_TO_PT);
    updateStyle({
      ...style,
      margins: {
        top: valPt,
        bottom: valPt,
        left: valPt,
        right: valPt,
        unit: 'pt',
      },
    });
  };

  const handleSpacingChange = (key: keyof typeof spacing, valPt: number) => {
    updateStyle({
      ...style,
      spacing: {
        ...style.spacing,
        [key]: valPt,
        unit: 'pt',
      },
    });
  };

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-5">
      <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
        <div className="p-2 bg-amber-50 text-amber-600 rounded-xl">
          <Move className="w-4 h-4" />
        </div>
        <div>
          <h3 className="font-bold text-sm text-slate-900">Margins & Spacing</h3>
          <p className="text-xs text-slate-500">Document margins (mm) and element vertical spacing (pt)</p>
        </div>
      </div>

      {/* 1. Margins Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-slate-700">Page Margins (mm)</label>
          <div className="flex items-center gap-1.5">
            {[
              { label: '8 mm (Compact)', mm: 8 },
              { label: '13 mm (Standard)', mm: 13 },
              { label: '18 mm (Wide)', mm: 18 },
            ].map((p) => (
              <button
                key={p.mm}
                type="button"
                onClick={() => handleApplyMarginPreset(p.mm)}
                className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Top & Bottom */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-600">Top & Bottom Margin</span>
            <span className="font-mono font-bold text-amber-700">{topMm} mm ({margins.top} pt)</span>
          </div>
          <input
            type="range"
            aria-label="Top and Bottom Margin"
            min={6}
            max={25}
            step={1}
            value={topMm}
            onChange={(e) => handleMarginChange('topBottom', Number(e.target.value))}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
          />
        </div>

        {/* Left & Right */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-600">Left & Right Margin</span>
            <span className="font-mono font-bold text-amber-700">{leftMm} mm ({margins.left} pt)</span>
          </div>
          <input
            type="range"
            aria-label="Left and Right Margin"
            min={8}
            max={28}
            step={1}
            value={leftMm}
            onChange={(e) => handleMarginChange('leftRight', Number(e.target.value))}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
          />
        </div>
      </div>

      {/* 2. Spacing Section */}
      <div className="space-y-3 pt-3 border-t border-slate-100">
        <label className="text-xs font-semibold text-slate-700">Element Spacing (pt)</label>

        {/* Section Spacing */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-600">Between Sections</span>
            <span className="font-mono font-bold text-amber-700">{spacing.sectionSpacing} pt</span>
          </div>
          <input
            type="range"
            aria-label="Spacing Between Sections"
            min={8}
            max={24}
            step={1}
            value={spacing.sectionSpacing}
            onChange={(e) => handleSpacingChange('sectionSpacing', Number(e.target.value))}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
          />
        </div>

        {/* Item Spacing */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-600">Between Items (Roles / Degrees)</span>
            <span className="font-mono font-bold text-amber-700">{spacing.itemSpacing} pt</span>
          </div>
          <input
            type="range"
            aria-label="Spacing Between Items"
            min={4}
            max={16}
            step={1}
            value={spacing.itemSpacing}
            onChange={(e) => handleSpacingChange('itemSpacing', Number(e.target.value))}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
          />
        </div>

        {/* Bullet Spacing */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-600">Between Bullets</span>
            <span className="font-mono font-bold text-amber-700">{spacing.bulletSpacing} pt</span>
          </div>
          <input
            type="range"
            aria-label="Spacing Between Bullets"
            min={1}
            max={8}
            step={0.5}
            value={spacing.bulletSpacing}
            onChange={(e) => handleSpacingChange('bulletSpacing', Number(e.target.value))}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
          />
        </div>

        {/* Header Bottom Spacing */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-600">Header Bottom Gap</span>
            <span className="font-mono font-bold text-amber-700">{spacing.headerBottomSpacing} pt</span>
          </div>
          <input
            type="range"
            aria-label="Header Bottom Gap Spacing"
            min={8}
            max={28}
            step={1}
            value={spacing.headerBottomSpacing}
            onChange={(e) => handleSpacingChange('headerBottomSpacing', Number(e.target.value))}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
          />
        </div>
      </div>
    </div>
  );
};

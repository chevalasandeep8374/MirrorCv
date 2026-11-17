'use client';

import React from 'react';
import { useResume } from '@/context/ResumeContext';
import { HeadingStyle } from '@/types/style';

const HEADING_STYLES: { id: HeadingStyle; label: string; previewClass: string }[] = [
  { id: 'underline', label: 'Underline', previewClass: 'border-b-2 border-blue-600 pb-0.5' },
  { id: 'bar', label: 'Accent Bar', previewClass: 'border-l-4 border-blue-600 pl-1.5' },
  { id: 'side_line', label: 'Side Line', previewClass: 'border-l-2 border-blue-600 pl-2' },
  { id: 'caps', label: 'Uppercase', previewClass: 'uppercase tracking-wider border-b border-slate-300 pb-0.5' },
  { id: 'boxed', label: 'Boxed', previewClass: 'bg-blue-600 text-white px-2 py-0.5 rounded text-[11px]' },
  { id: 'pill', label: 'Pill', previewClass: 'bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full text-[11px]' },
  { id: 'plain', label: 'Plain', previewClass: 'font-bold' },
];

export const SectionHeadingsCard: React.FC = () => {
  const { style, updateStyle } = useResume();

  const currentStyle = style.headingStyle;
  const currentHeading = style.heading || {
    capitalization: 'none',
    iconStyle: 'none',
  };

  const handleStyleChange = (s: HeadingStyle) => {
    updateStyle({
      ...style,
      headingStyle: s,
    });
  };

  const handleCapitalizationChange = (cap: 'none' | 'capitalize' | 'uppercase') => {
    updateStyle({
      ...style,
      heading: {
        ...currentHeading,
        capitalization: cap,
      },
    });
  };

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-5">
      <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
        <div className="p-2 bg-rose-50 text-rose-600 rounded-xl">
          <span className="font-black text-sm">H2</span>
        </div>
        <div>
          <h3 className="font-bold text-sm text-slate-900">Section Headings</h3>
          <p className="text-xs text-slate-500">Visual heading accents, decoration, and capitalization</p>
        </div>
      </div>

      {/* 1. Heading Styles Grid */}
      <div className="space-y-2">
        <label className="text-xs font-semibold text-slate-700">Heading Style</label>
        <div className="grid grid-cols-2 gap-2">
          {HEADING_STYLES.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => handleStyleChange(item.id)}
              className={`p-3 rounded-xl border text-left transition-all ${
                currentStyle === item.id
                  ? 'border-rose-600 bg-rose-50/40 text-rose-950 font-bold shadow-xs'
                  : 'border-slate-200 hover:border-slate-300 text-slate-700'
              }`}
            >
              <div className="text-xs font-bold mb-1.5">{item.label}</div>
              <div className="text-xs font-semibold text-slate-800">
                <span className={item.previewClass}>Experience</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 2. Capitalization */}
      <div className="space-y-2 pt-2 border-t border-slate-100">
        <label className="text-xs font-semibold text-slate-700">Heading Capitalization</label>
        <div className="grid grid-cols-3 gap-2">
          {[
            { id: 'none', label: 'As Typed (Natural)' },
            { id: 'capitalize', label: 'Title Case' },
            { id: 'uppercase', label: 'UPPERCASE' },
          ].map((c) => (
            <button
              key={c.id}
              type="button"
              onClick={() => handleCapitalizationChange(c.id as any)}
              className={`py-2 px-2 rounded-xl border text-center text-xs font-medium transition-all ${
                currentHeading.capitalization === c.id
                  ? 'border-rose-600 bg-rose-50/40 text-rose-900 font-bold shadow-xs'
                  : 'border-slate-200 hover:border-slate-300 text-slate-700'
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

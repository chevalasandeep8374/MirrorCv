'use client';

import React, { useState } from 'react';
import { useResume } from '@/context/ResumeContext';
import { Sparkles, Check } from 'lucide-react';

export const CURATED_FONTS = [
  // Sans-serif
  { name: 'Inter', category: 'Sans', character: 'Clean, modern UI standard' },
  { name: 'Roboto', category: 'Sans', character: 'Corporate tech standard' },
  { name: 'Open Sans', category: 'Sans', character: 'Neutral & legible at small sizes' },
  { name: 'Lato', category: 'Sans', character: 'Warm, semi-rounded details' },
  { name: 'Montserrat', category: 'Sans', character: 'Architectural, geometric headers' },
  { name: 'Source Sans 3', category: 'Sans', character: "Adobe's clean editorial sans" },
  { name: 'Poppins', category: 'Sans', character: 'Friendly geometric headings' },
  { name: 'Nunito', category: 'Sans', character: 'Modern, creative and approachable' },
  { name: 'Raleway', category: 'Sans', character: 'High-end minimal aesthetics' },
  { name: 'Fira Sans', category: 'Sans', character: 'Engineering & technical resumes' },

  // Serif
  { name: 'Merriweather', category: 'Serif', character: 'Screen-optimized editorial serif' },
  { name: 'Playfair Display', category: 'Serif', character: 'Sophisticated executive headings' },
  { name: 'Lora', category: 'Serif', character: 'Literary, elegant body serif' },
  { name: 'PT Serif', category: 'Serif', character: 'Formal academic & legal standard' },
  { name: 'Cinzel', category: 'Serif', character: 'Classical monumental headers' },

  // Multilingual
  { name: 'Noto Sans Devanagari', category: 'Multilingual', character: 'Devanagari / Hindi standard' },
];

export const FontPickerCard: React.FC = () => {
  const { style, updateStyle } = useResume();
  const [targetRole, setTargetRole] = useState<'base' | 'heading' | 'name'>('base');

  const typography = style.typography;
  const currentBase = typography.baseFontFamily || 'Inter';
  const currentHeading = typography.headingFontFamily || 'Inter';
  const currentName = typography.nameFontFamily || currentHeading;

  const handleSelectFont = (fontName: string) => {
    if (targetRole === 'base') {
      updateStyle({
        ...style,
        typography: {
          ...style.typography,
          baseFontFamily: fontName,
        },
      });
    } else if (targetRole === 'heading') {
      updateStyle({
        ...style,
        typography: {
          ...style.typography,
          headingFontFamily: fontName,
        },
      });
    } else {
      updateStyle({
        ...style,
        typography: {
          ...style.typography,
          nameFontFamily: fontName,
        },
      });
    }
  };

  const getActiveFontForTarget = () => {
    if (targetRole === 'base') return currentBase;
    if (targetRole === 'heading') return currentHeading;
    return currentName;
  };

  const activeFont = getActiveFontForTarget();

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-5">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-emerald-50 text-emerald-600 rounded-xl">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-slate-900">Self-Hosted Fonts</h3>
            <p className="text-xs text-slate-500">15 curated open fonts (Zero third-party CDN)</p>
          </div>
        </div>
      </div>

      {/* Target Role Selector */}
      <div className="flex items-center gap-2 p-1 bg-slate-100 rounded-xl">
        {[
          { id: 'base', label: 'Body Text', activeFont: currentBase },
          { id: 'heading', label: 'Headings', activeFont: currentHeading },
          { id: 'name', label: 'Name', activeFont: currentName },
        ].map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setTargetRole(tab.id as any)}
            className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold transition-all ${
              targetRole === tab.id
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <div>{tab.label}</div>
            <div className="text-[10px] text-slate-400 font-normal truncate">{tab.activeFont}</div>
          </button>
        ))}
      </div>

      {/* Font Swatch List */}
      <div
        tabIndex={0}
        role="region"
        aria-label="Available Fonts List"
        className="space-y-2 max-h-72 overflow-y-auto pr-1 focus:outline-hidden focus:ring-1 focus:ring-emerald-500 rounded-lg"
      >
        {CURATED_FONTS.map((font) => {
          const isSelected = activeFont === font.name;

          return (
            <div
              key={font.name}
              onClick={() => handleSelectFont(font.name)}
              className={`group cursor-pointer p-3 rounded-xl border transition-all flex items-center justify-between ${
                isSelected
                  ? 'border-emerald-600 bg-emerald-50/40 shadow-xs'
                  : 'border-slate-200 hover:border-slate-300 bg-white'
              }`}
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span
                    className="text-base text-slate-900 font-medium"
                    style={{ fontFamily: font.name }}
                  >
                    {font.name}
                  </span>
                  <span className="text-[9px] font-bold uppercase tracking-wider text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">
                    {font.category}
                  </span>
                </div>
                <div
                  className="text-xs text-slate-500 mt-1 truncate"
                  style={{ fontFamily: font.name }}
                >
                  Quick brown fox jumps over the lazy dog
                </div>
              </div>

              {isSelected && (
                <div className="p-1 bg-emerald-600 text-white rounded-full shrink-0 ml-2">
                  <Check className="w-3.5 h-3.5" />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

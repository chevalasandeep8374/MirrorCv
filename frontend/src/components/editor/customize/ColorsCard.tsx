'use client';

import React from 'react';
import { useResume } from '@/context/ResumeContext';
import { Palette, AlertCircle, CheckCircle2, ShieldAlert } from 'lucide-react';
import { Colors, AccentToggles } from '@/types/style';
import { getContrastRatio, evaluateWcag } from '@/lib/contrast';

export interface ColorPatternPreset {
  id: string;
  name: string;
  category: string;
  accent: string;
  text: string;
  muted: string;
  background: string;
  sidebarBackground: string;
  divider: string;
}

export const COLOR_PATTERNS: ColorPatternPreset[] = [
  {
    id: 'modern-indigo',
    name: 'Modern Tech Indigo',
    category: 'AI & Engineering',
    accent: '#4F46E5',
    text: '#0F172A',
    muted: '#64748B',
    background: '#FFFFFF',
    sidebarBackground: '#F8FAFC',
    divider: '#E2E8F0',
  },
  {
    id: 'executive-navy',
    name: 'Classic Executive Navy',
    category: 'Corporate & Finance',
    accent: '#1E3A8A',
    text: '#111827',
    muted: '#4B5563',
    background: '#FFFFFF',
    sidebarBackground: '#F9FAFB',
    divider: '#E5E7EB',
  },
  {
    id: 'deep-teal',
    name: 'Deep Ocean Teal',
    category: 'Modern Tech',
    accent: '#0D9488',
    text: '#0F172A',
    muted: '#64748B',
    background: '#FFFFFF',
    sidebarBackground: '#F0FDFA',
    divider: '#CCFBF1',
  },
  {
    id: 'forest-emerald',
    name: 'Forest Emerald',
    category: 'Fresh & Balanced',
    accent: '#059669',
    text: '#0F172A',
    muted: '#475569',
    background: '#FFFFFF',
    sidebarBackground: '#F0FDF4',
    divider: '#E2E8F0',
  },
  {
    id: 'executive-crimson',
    name: 'Executive Crimson',
    category: 'Leadership & Bold',
    accent: '#BE123C',
    text: '#18181B',
    muted: '#71717A',
    background: '#FFFFFF',
    sidebarBackground: '#FFF1F2',
    divider: '#FECDD3',
  },
  {
    id: 'slate-monochrome',
    name: 'Minimalist Slate Monochrome',
    category: 'High ATS & Clean Print',
    accent: '#334155',
    text: '#0F172A',
    muted: '#64748B',
    background: '#FFFFFF',
    sidebarBackground: '#F8FAFC',
    divider: '#E2E8F0',
  },
  {
    id: 'royal-blue',
    name: 'Royal Blue Standard',
    category: 'Classic Tech',
    accent: '#2563EB',
    text: '#111827',
    muted: '#4B5563',
    background: '#FFFFFF',
    sidebarBackground: '#F8FAFC',
    divider: '#E5E7EB',
  },
  {
    id: 'imperial-violet',
    name: 'Imperial Violet',
    category: 'Creative Tech',
    accent: '#7C3AED',
    text: '#1E1B4B',
    muted: '#6B7280',
    background: '#FFFFFF',
    sidebarBackground: '#F5F3FF',
    divider: '#EDE9FE',
  },
];

const CURATED_PALETTE = [
  { name: 'Royal Blue', hex: '#2563eb' },
  { name: 'Deep Teal', hex: '#0f766e' },
  { name: 'Forest Emerald', hex: '#059669' },
  { name: 'Modern Indigo', hex: '#4f46e5' },
  { name: 'Imperial Violet', hex: '#7c3aed' },
  { name: 'Executive Crimson', hex: '#e11d48' },
  { name: 'Warm Amber', hex: '#d97706' },
  { name: 'Charcoal Slate', hex: '#334155' },
];

export const ColorsCard: React.FC = () => {
  const { style, updateStyle } = useResume();

  const colors = style.colors;
  const accentToggles = colors.accentToggles || {
    name: false,
    jobTitle: false,
    headings: true,
    headingsLine: true,
    headerIcons: true,
    bullets: true,
    dates: false,
    entryTitle: false,
    entrySubtitle: false,
    linkIcons: true,
  };

  const handleColorChange = (key: keyof Colors, value: string) => {
    updateStyle({
      ...style,
      colors: {
        ...colors,
        [key]: value,
      },
    });
  };

  const applyColorPattern = (preset: ColorPatternPreset) => {
    updateStyle({
      ...style,
      colors: {
        ...colors,
        accent: preset.accent,
        text: preset.text,
        muted: preset.muted,
        background: preset.background,
        sidebarBackground: preset.sidebarBackground,
        divider: preset.divider,
      },
    });
  };

  const handleToggleAccent = (key: keyof AccentToggles, value: boolean) => {
    updateStyle({
      ...style,
      colors: {
        ...colors,
        accentToggles: {
          ...accentToggles,
          [key]: value,
        },
      },
    });
  };

  // WCAG Contrast Checks
  const textContrast = getContrastRatio(colors.text, colors.background);
  const textWcag = evaluateWcag(textContrast);
  const accentContrast = getContrastRatio(colors.accent, colors.background);
  const accentWcag = evaluateWcag(accentContrast);

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-5">
      <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
        <div className="p-2 bg-pink-50 text-pink-600 rounded-xl">
          <Palette className="w-4 h-4" />
        </div>
        <div>
          <h3 className="font-bold text-sm text-slate-900">Color Palette & Accents</h3>
          <p className="text-xs text-slate-500">Theme colors, granular accent toggles, and WCAG contrast check</p>
        </div>
      </div>

      {/* 1. Complete Color Theme Patterns */}
      <div className="space-y-2.5">
        <div className="flex items-center justify-between">
          <label className="text-xs font-bold text-slate-800">Curated Color Patterns</label>
          <span className="text-[10px] text-slate-400 font-medium">1-Click Apply</span>
        </div>
        <div className="grid grid-cols-2 gap-2">
          {COLOR_PATTERNS.map((p) => {
            const isSelected =
              colors.accent.toLowerCase() === p.accent.toLowerCase() &&
              colors.text.toLowerCase() === p.text.toLowerCase();
            return (
              <button
                key={p.id}
                type="button"
                onClick={() => applyColorPattern(p)}
                className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer flex flex-col gap-1.5 ${
                  isSelected
                    ? 'border-blue-600 bg-blue-50/50 shadow-2xs ring-1 ring-blue-600'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/60'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-slate-900 truncate">{p.name}</span>
                  {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0" />}
                </div>
                <div className="flex items-center gap-1.5">
                  <div
                    className="w-4 h-4 rounded-full border border-slate-200 shadow-2xs shrink-0"
                    style={{ backgroundColor: p.accent }}
                    title={`Accent: ${p.accent}`}
                  />
                  <div
                    className="w-4 h-4 rounded-full border border-slate-200 shadow-2xs shrink-0"
                    style={{ backgroundColor: p.text }}
                    title={`Text: ${p.text}`}
                  />
                  <div
                    className="w-4 h-4 rounded-full border border-slate-200 shadow-2xs shrink-0"
                    style={{ backgroundColor: p.muted }}
                    title={`Muted: ${p.muted}`}
                  />
                  <span className="text-[10px] text-slate-400 truncate ml-auto">{p.category}</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. Curated Quick Single Color Accents */}
      <div className="space-y-2 pt-2 border-t border-slate-100">
        <label className="text-xs font-semibold text-slate-700">Quick Single Accent</label>
        <div className="flex flex-wrap gap-2">
          {CURATED_PALETTE.map((c) => (
            <button
              key={c.hex}
              type="button"
              onClick={() => handleColorChange('accent', c.hex)}
              title={`${c.name} (${c.hex})`}
              className={`w-7 h-7 rounded-full border-2 transition-transform hover:scale-110 flex items-center justify-center ${
                colors.accent.toLowerCase() === c.hex.toLowerCase()
                  ? 'border-slate-900 ring-2 ring-slate-400'
                  : 'border-white shadow-xs'
              }`}
              style={{ backgroundColor: c.hex }}
            />
          ))}
        </div>
      </div>

      {/* 2. Color Inputs */}
      <div className="grid grid-cols-2 gap-3">
        {/* Accent */}
        <div className="space-y-1">
          <label className="text-[11px] font-semibold text-slate-600">Accent Color</label>
          <div className="flex items-center gap-2 border border-slate-200 rounded-xl p-1.5 bg-slate-50">
            <input
              type="color"
              aria-label="Accent Color Picker"
              value={colors.accent}
              onChange={(e) => handleColorChange('accent', e.target.value)}
              className="w-7 h-7 rounded-lg border-0 cursor-pointer bg-transparent"
            />
            <input
              type="text"
              aria-label="Accent Color Hex"
              value={colors.accent}
              onChange={(e) => handleColorChange('accent', e.target.value)}
              className="text-xs font-mono font-medium text-slate-800 bg-transparent w-full focus:outline-hidden"
            />
          </div>
        </div>

        {/* Text */}
        <div className="space-y-1">
          <label className="text-[11px] font-semibold text-slate-600">Text Color</label>
          <div className="flex items-center gap-2 border border-slate-200 rounded-xl p-1.5 bg-slate-50">
            <input
              type="color"
              aria-label="Text Color Picker"
              value={colors.text}
              onChange={(e) => handleColorChange('text', e.target.value)}
              className="w-7 h-7 rounded-lg border-0 cursor-pointer bg-transparent"
            />
            <input
              type="text"
              aria-label="Text Color Hex"
              value={colors.text}
              onChange={(e) => handleColorChange('text', e.target.value)}
              className="text-xs font-mono font-medium text-slate-800 bg-transparent w-full focus:outline-hidden"
            />
          </div>
        </div>

        {/* Background */}
        <div className="space-y-1">
          <label className="text-[11px] font-semibold text-slate-600">Background</label>
          <div className="flex items-center gap-2 border border-slate-200 rounded-xl p-1.5 bg-slate-50">
            <input
              type="color"
              aria-label="Background Color Picker"
              value={colors.background}
              onChange={(e) => handleColorChange('background', e.target.value)}
              className="w-7 h-7 rounded-lg border-0 cursor-pointer bg-transparent"
            />
            <input
              type="text"
              aria-label="Background Color Hex"
              value={colors.background}
              onChange={(e) => handleColorChange('background', e.target.value)}
              className="text-xs font-mono font-medium text-slate-800 bg-transparent w-full focus:outline-hidden"
            />
          </div>
        </div>

        {/* Sidebar Background */}
        <div className="space-y-1">
          <label className="text-[11px] font-semibold text-slate-600">Sidebar Background</label>
          <div className="flex items-center gap-2 border border-slate-200 rounded-xl p-1.5 bg-slate-50">
            <input
              type="color"
              aria-label="Sidebar Background Color Picker"
              value={colors.sidebarBackground}
              onChange={(e) => handleColorChange('sidebarBackground', e.target.value)}
              className="w-7 h-7 rounded-lg border-0 cursor-pointer bg-transparent"
            />
            <input
              type="text"
              aria-label="Sidebar Background Color Hex"
              value={colors.sidebarBackground}
              onChange={(e) => handleColorChange('sidebarBackground', e.target.value)}
              className="text-xs font-mono font-medium text-slate-800 bg-transparent w-full focus:outline-hidden"
            />
          </div>
        </div>
      </div>

      {/* 3. WCAG Accessibility Warning */}
      <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1.5 text-xs">
        <div className="font-semibold text-slate-700 flex items-center justify-between">
          <span>Readability & Contrast</span>
          <span
            className={`font-mono text-[10px] px-2 py-0.5 rounded font-bold ${
              textWcag.normalAa
                ? 'bg-emerald-100 text-emerald-800'
                : 'bg-amber-100 text-amber-800'
            }`}
          >
            Ratio: {textContrast.toFixed(1)}:1 ({textWcag.ratingText})
          </span>
        </div>
        {!textWcag.normalAa && (
          <div className="flex items-center gap-1.5 text-[11px] text-amber-700 font-medium">
            <AlertCircle className="w-3.5 h-3.5 shrink-0" />
            <span>Low contrast between text and background. May hurt ATS scanning and readability.</span>
          </div>
        )}
      </div>

      {/* 4. Granular Accent Toggles */}
      <div className="space-y-2 pt-2 border-t border-slate-100">
        <label className="text-xs font-semibold text-slate-700">Apply Accent Color To</label>
        <div className="grid grid-cols-2 gap-2 text-xs">
          {[
            { key: 'headings', label: 'Section Headings' },
            { key: 'headingsLine', label: 'Heading Lines / Bars' },
            { key: 'bullets', label: 'List Bullets' },
            { key: 'linkIcons', label: 'Contact Links' },
            { key: 'headerIcons', label: 'Header Icons' },
            { key: 'dates', label: 'Dates & Timeframes' },
            { key: 'entryTitle', label: 'Role & Degree Titles' },
            { key: 'entrySubtitle', label: 'Company Subtitles' },
            { key: 'name', label: 'Candidate Name' },
            { key: 'jobTitle', label: 'Candidate Job Title' },
          ].map((item) => (
            <label
              key={item.key}
              className="flex items-center gap-2 p-2 rounded-xl border border-slate-100 hover:bg-slate-50 cursor-pointer select-none"
            >
              <input
                type="checkbox"
                checked={Boolean((accentToggles as any)[item.key])}
                onChange={(e) => handleToggleAccent(item.key as any, e.target.checked)}
                className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300"
              />
              <span className="text-slate-700 text-[11px]">{item.label}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
};

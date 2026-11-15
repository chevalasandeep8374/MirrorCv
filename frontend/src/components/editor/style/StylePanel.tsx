'use client';

import React, { useState, useEffect } from 'react';
import { useResume } from '@/context/ResumeContext';
import { TEMPLATE_PRESETS } from '@/lib/presets';
import {
  PageSize,
  BulletStyle,
  HeadingStyle,
  ColumnLayoutType,
  ResumeStyle,
} from '@/types/style';
import { getContrastRatio, evaluateWcag } from '@/lib/contrast';
import { apiClient } from '@/lib/api';
import {
  Palette,
  Layout,
  Type,
  Move,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  BookmarkPlus,
  ArrowRightLeft,
  Calendar,
  Sparkles,
  Globe,
} from 'lucide-react';
import {
  SUPPORTED_LOCALES,
  SECTION_TRANSLATIONS,
  SupportedLocale,
  getLocaleDirection,
} from '@/lib/i18n';

export const StylePanel: React.FC = () => {
  const { style, content, updateStyle, applyPreset, updateContent } = useResume();
  const [saveModalOpen, setSaveModalOpen] = useState(false);
  const [presetName, setPresetName] = useState('');
  const [presetDescription, setPresetDescription] = useState('');
  const [presetCategory, setPresetCategory] = useState('single');
  const [savingPreset, setSavingPreset] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleUpdate = (patch: Partial<ResumeStyle>) => {
    updateStyle({
      ...style,
      ...patch,
    });
  };

  const handleTypographyUpdate = (patch: Partial<ResumeStyle['typography']>) => {
    updateStyle({
      ...style,
      typography: {
        ...style.typography,
        ...patch,
      },
    });
  };

  const handleFontSizesUpdate = (patch: Partial<ResumeStyle['typography']['fontSizes']>) => {
    updateStyle({
      ...style,
      typography: {
        ...style.typography,
        fontSizes: {
          ...style.typography.fontSizes,
          ...patch,
        },
      },
    });
  };

  const handleSpacingUpdate = (patch: Partial<ResumeStyle['spacing']>) => {
    updateStyle({
      ...style,
      spacing: {
        ...style.spacing,
        ...patch,
      },
    });
  };

  const handleMarginsUpdate = (patch: Partial<ResumeStyle['margins']>) => {
    updateStyle({
      ...style,
      margins: {
        ...style.margins,
        ...patch,
      },
    });
  };

  const handleColorsUpdate = (patch: Partial<ResumeStyle['colors']>) => {
    updateStyle({
      ...style,
      colors: {
        ...style.colors,
        ...patch,
      },
    });
  };

  const handleLayoutUpdate = (patch: Partial<ResumeStyle['layout']>) => {
    updateStyle({
      ...style,
      layout: {
        ...style.layout,
        ...patch,
      },
    });
  };

  // Section column overrides (move section between Main and Sidebar)
  const toggleSectionColumn = (sectionId: string) => {
    const isCurrentlySidebar = style.layout.sidebarSectionIds.includes(sectionId);
    let newSidebar = [...style.layout.sidebarSectionIds];
    let newMain = [...style.layout.mainSectionIds];

    if (isCurrentlySidebar) {
      newSidebar = newSidebar.filter((id) => id !== sectionId);
      if (!newMain.includes(sectionId)) newMain.push(sectionId);
    } else {
      newMain = newMain.filter((id) => id !== sectionId);
      if (!newSidebar.includes(sectionId)) newSidebar.push(sectionId);
    }

    handleLayoutUpdate({
      sidebarSectionIds: newSidebar,
      mainSectionIds: newMain,
    });
  };

  // Safe preset apply that preserves all content
  const handleApplyPresetSafe = (newPreset: ResumeStyle) => {
    // Check if any section would be excluded
    const allSectionIds = content.sections.map((s) => s.id);
    const isSidebarType =
      newPreset.layout.type === 'sidebar_left' ||
      newPreset.layout.type === 'sidebar_right';

    let adjustedLayout = { ...newPreset.layout };

    if (!isSidebarType) {
      adjustedLayout.mainSectionIds = allSectionIds;
      adjustedLayout.sidebarSectionIds = [];
    } else {
      // Keep sections in newPreset's sidebar if present, otherwise put into main
      const sidebarSet = new Set(newPreset.layout.sidebarSectionIds);
      const mainSet = new Set(newPreset.layout.mainSectionIds);

      allSectionIds.forEach((id) => {
        if (!sidebarSet.has(id) && !mainSet.has(id)) {
          adjustedLayout.mainSectionIds.push(id);
        }
      });
    }

    applyPreset({
      ...newPreset,
      layout: adjustedLayout,
    });

    showToast(`Applied preset: ${newPreset.templateId}`);
  };

  // Save current style as user preset
  const handleSaveUserPreset = async () => {
    if (!presetName.trim()) return;
    setSavingPreset(true);
    try {
      await apiClient.post('/templates/user-presets', {
        name: presetName.trim(),
        description: presetDescription.trim() || 'Custom user style preset',
        category: presetCategory,
        style,
      });
      setSaveModalOpen(false);
      setPresetName('');
      setPresetDescription('');
      showToast('Custom template saved to your library!');
    } catch (err) {
      console.error('Failed to save preset:', err);
      alert('Could not save preset. Please verify connection or login.');
    } finally {
      setSavingPreset(false);
    }
  };

  // Evaluate WCAG contrast for text on background
  const textContrast = getContrastRatio(style.colors.text, style.colors.background);
  const wcagEvaluation = evaluateWcag(textContrast);

  const openFonts = [
    { label: 'Inter (Clean Sans)', value: 'Inter' },
    { label: 'Liberation Sans (Arial Metric-Match)', value: 'Liberation Sans' },
    { label: 'Liberation Serif (Times Metric-Match)', value: 'Liberation Serif' },
    { label: 'Montserrat (Modern Geometric)', value: 'Montserrat' },
    { label: 'Roboto (Neutral Sans)', value: 'Roboto' },
    { label: 'Merriweather (Editorial Serif)', value: 'Merriweather' },
    { label: 'Cinzel (Classical Academic)', value: 'Cinzel' },
  ];

  const colorPresets = [
    '#2563eb', // Royal Blue
    '#0f766e', // Deep Teal
    '#7c3aed', // Purple
    '#dc2626', // Crimson Red
    '#d97706', // Amber
    '#059669', // Emerald
    '#1e293b', // Slate Dark
    '#09090b', // Pitch Black
  ];

  return (
    <div className="p-4 pb-24 overflow-y-auto max-h-full space-y-6 text-xs text-slate-700">
      {/* Toast message */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-900 text-white px-4 py-2.5 rounded-xl shadow-xl flex items-center gap-2 text-xs font-semibold animate-in fade-in slide-in-from-bottom-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* 1. Template Presets Picker & Save Button */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1.5 font-bold uppercase text-[11px] text-slate-500 tracking-wider">
            <Palette className="w-3.5 h-3.5 text-blue-600" />
            <span>Templates & Presets</span>
          </div>

          <button
            type="button"
            onClick={() => setSaveModalOpen(true)}
            className="inline-flex items-center gap-1 text-[11px] font-bold text-blue-600 hover:text-blue-800 transition-colors"
          >
            <BookmarkPlus className="w-3.5 h-3.5" />
            <span>Save As My Template</span>
          </button>
        </div>

        <div className="grid grid-cols-2 gap-2">
          {TEMPLATE_PRESETS.map((preset) => {
            const isSelected = style.templateId === preset.id;
            return (
              <button
                key={preset.id}
                type="button"
                onClick={() => handleApplyPresetSafe(preset.style)}
                className={`p-2.5 rounded-xl border text-left transition-all ${
                  isSelected
                    ? 'border-blue-600 bg-blue-50/60 shadow-xs ring-1 ring-blue-500'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <div className="font-bold text-slate-900 text-xs flex items-center justify-between">
                  <span className="truncate">{preset.name}</span>
                  {isSelected && (
                    <span className="text-[9px] text-blue-600 font-bold bg-blue-100 px-1 py-0.2 rounded shrink-0">
                      Active
                    </span>
                  )}
                </div>
                <p className="text-[10px] text-slate-500 mt-0.5 line-clamp-1">
                  {preset.category}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. Layout, Columns, & Dimensions */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 space-y-3">
        <div className="flex items-center space-x-1.5 font-bold uppercase text-[11px] text-slate-500 tracking-wider">
          <Layout className="w-3.5 h-3.5 text-blue-600" />
          <span>Layout & Dimensions</span>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Page Size
            </label>
            <select
              value={style.pageSize}
              onChange={(e) => handleUpdate({ pageSize: e.target.value as PageSize })}
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white font-medium"
            >
              <option value="A4">A4 (210 x 297 mm)</option>
              <option value="Letter">US Letter (8.5 x 11 in)</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Column Layout
            </label>
            <select
              value={style.layout.type}
              onChange={(e) =>
                handleLayoutUpdate({ type: e.target.value as ColumnLayoutType })
              }
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white font-medium"
            >
              <option value="single">Single Column</option>
              <option value="sidebar_left">Sidebar on Left</option>
              <option value="sidebar_right">Sidebar on Right</option>
              <option value="header_banner">Header Banner Card</option>
              <option value="compact">Compact Technical</option>
              <option value="creative">Creative Accent</option>
              <option value="minimal">Minimal Editorial</option>
              <option value="academic">Academic CV</option>
            </select>
          </div>
        </div>

        {(style.layout.type === 'sidebar_left' || style.layout.type === 'sidebar_right') && (
          <div className="pt-2 border-t border-slate-100 space-y-3">
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-[11px] font-semibold text-slate-600">
                  Sidebar Width: {style.layout.sidebarWidthPercent}%
                </label>
              </div>
              <input
                type="range"
                min={20}
                max={50}
                step={1}
                value={style.layout.sidebarWidthPercent}
                onChange={(e) =>
                  handleLayoutUpdate({ sidebarWidthPercent: Number(e.target.value) })
                }
                className="w-full accent-blue-600"
              />
            </div>

            {/* Section Column Assignments */}
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1.5">
                Section Column Placement
              </label>
              <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                {content.sections.map((section) => {
                  const inSidebar = style.layout.sidebarSectionIds.includes(section.id);
                  return (
                    <div
                      key={section.id}
                      className="flex items-center justify-between p-1.5 rounded-lg bg-slate-50 border border-slate-200"
                    >
                      <span className="font-medium text-slate-800 text-[11px] truncate">
                        {section.title}
                      </span>
                      <button
                        type="button"
                        onClick={() => toggleSectionColumn(section.id)}
                        className={`text-[10px] font-bold px-2 py-0.5 rounded transition-all flex items-center gap-1 ${
                          inSidebar
                            ? 'bg-purple-100 text-purple-700 hover:bg-purple-200'
                            : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                        }`}
                      >
                        <ArrowRightLeft className="w-2.5 h-2.5" />
                        <span>{inSidebar ? 'Sidebar' : 'Main'}</span>
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Language, i18n & RTL Configuration */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 space-y-3">
        <div className="flex items-center space-x-1.5 font-bold uppercase text-[11px] text-slate-500 tracking-wider">
          <Globe className="w-3.5 h-3.5 text-blue-600" />
          <span>Language, i18n & Direction</span>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Resume Language
            </label>
            <select
              value={style.locale || 'en'}
              onChange={(e) => {
                const loc = e.target.value as SupportedLocale;
                const dir = getLocaleDirection(loc);
                handleUpdate({ locale: loc, direction: dir });
              }}
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white font-medium text-xs"
            >
              {Object.values(SUPPORTED_LOCALES).map((loc) => (
                <option key={loc.code} value={loc.code}>
                  {loc.nativeName} ({loc.name}) {loc.direction === 'rtl' ? '— RTL' : ''}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Text Direction
            </label>
            <select
              value={style.direction || getLocaleDirection(style.locale)}
              onChange={(e) =>
                handleUpdate({ direction: e.target.value as 'ltr' | 'rtl' })
              }
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white font-medium text-xs"
            >
              <option value="ltr">Left-to-Right (LTR)</option>
              <option value="rtl">Right-to-Left (RTL - Arabic, Hebrew)</option>
            </select>
          </div>
        </div>

        <button
          type="button"
          onClick={() => {
            const loc = (style.locale || 'en') as SupportedLocale;
            const trans = SECTION_TRANSLATIONS[loc];
            if (trans) {
              const nextSections = content.sections.map((s) => ({
                ...s,
                title: trans[s.type] || s.title,
              }));
              updateContent({ ...content, sections: nextSections });
              showToast(`Translated section titles to ${SUPPORTED_LOCALES[loc].name}`);
            }
          }}
          className="w-full py-1.5 px-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-semibold text-[11px] transition-colors flex items-center justify-center gap-1.5"
        >
          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
          <span>Translate Section Titles to {SUPPORTED_LOCALES[style.locale || 'en']?.name || 'Selected Language'}</span>
        </button>
      </div>

      {/* 3. Typography & Per-Role Fonts */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 space-y-3">
        <div className="flex items-center space-x-1.5 font-bold uppercase text-[11px] text-slate-500 tracking-wider">
          <Type className="w-3.5 h-3.5 text-blue-600" />
          <span>Typography & Self-Hosted Fonts</span>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Body & Details Font
            </label>
            <select
              value={style.typography.baseFontFamily}
              onChange={(e) => handleTypographyUpdate({ baseFontFamily: e.target.value })}
              className="w-full px-2 py-1.5 border border-slate-200 rounded-lg bg-white text-[11px]"
            >
              {openFonts.map((f) => (
                <option key={f.value} value={f.value}>
                  {f.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Heading Font
            </label>
            <select
              value={style.typography.headingFontFamily}
              onChange={(e) =>
                handleTypographyUpdate({ headingFontFamily: e.target.value })
              }
              className="w-full px-2 py-1.5 border border-slate-200 rounded-lg bg-white text-[11px]"
            >
              {openFonts.map((f) => (
                <option key={f.value} value={f.value}>
                  {f.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-[11px] font-semibold text-slate-600 mb-1">
            Name / Title Font
          </label>
          <select
            value={style.typography.nameFontFamily || style.typography.headingFontFamily}
            onChange={(e) =>
              handleTypographyUpdate({ nameFontFamily: e.target.value })
            }
            className="w-full px-2 py-1.5 border border-slate-200 rounded-lg bg-white text-[11px]"
          >
            {openFonts.map((f) => (
              <option key={f.value} value={f.value}>
                {f.label}
              </option>
            ))}
          </select>
        </div>

        {/* Font Scale & Line Height */}
        <div className="space-y-2.5 pt-2 border-t border-slate-100">
          <div>
            <div className="flex justify-between items-center mb-0.5">
              <span className="text-[11px] font-semibold text-slate-600">
                Font Size Scale: {(style.typography.fontSizeScale ?? 1.0).toFixed(2)}x
              </span>
            </div>
            <input
              type="range"
              min={0.8}
              max={1.3}
              step={0.02}
              value={style.typography.fontSizeScale ?? 1.0}
              onChange={(e) =>
                handleTypographyUpdate({ fontSizeScale: Number(e.target.value) })
              }
              className="w-full accent-blue-600"
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-0.5">
              <span className="text-[11px] font-semibold text-slate-600">
                Line Height: {style.typography.lineHeight}
              </span>
            </div>
            <input
              type="range"
              min={1.1}
              max={2.0}
              step={0.05}
              value={style.typography.lineHeight}
              onChange={(e) =>
                handleTypographyUpdate({ lineHeight: Number(e.target.value) })
              }
              className="w-full accent-blue-600"
            />
          </div>
        </div>
      </div>

      {/* 4. Colors & Contrast Check */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 space-y-3">
        <div className="flex items-center space-x-1.5 font-bold uppercase text-[11px] text-slate-500 tracking-wider">
          <Palette className="w-3.5 h-3.5 text-blue-600" />
          <span>Colors & WCAG Contrast</span>
        </div>

        <div>
          <label className="block text-[11px] font-semibold text-slate-600 mb-1.5">
            Accent Color
          </label>
          <div className="flex items-center space-x-2">
            <input
              type="color"
              value={style.colors.accent}
              onChange={(e) => handleColorsUpdate({ accent: e.target.value })}
              className="w-8 h-8 rounded border border-slate-200 cursor-pointer p-0.5"
            />
            <input
              type="text"
              value={style.colors.accent}
              onChange={(e) => handleColorsUpdate({ accent: e.target.value })}
              className="w-24 px-2 py-1 border border-slate-200 rounded uppercase font-mono text-xs"
            />
            <div className="flex items-center space-x-1 ml-auto">
              {colorPresets.map((c) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => handleColorsUpdate({ accent: c })}
                  style={{ backgroundColor: c }}
                  className="w-4 h-4 rounded-full ring-1 ring-slate-200 hover:scale-125 transition-transform"
                />
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Text Color
            </label>
            <div className="flex items-center space-x-1.5">
              <input
                type="color"
                value={style.colors.text}
                onChange={(e) => handleColorsUpdate({ text: e.target.value })}
                className="w-7 h-7 rounded border border-slate-200 cursor-pointer p-0.5"
              />
              <span className="text-[11px] font-mono text-slate-600">{style.colors.text}</span>
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Background Color
            </label>
            <div className="flex items-center space-x-1.5">
              <input
                type="color"
                value={style.colors.background}
                onChange={(e) => handleColorsUpdate({ background: e.target.value })}
                className="w-7 h-7 rounded border border-slate-200 cursor-pointer p-0.5"
              />
              <span className="text-[11px] font-mono text-slate-600">
                {style.colors.background}
              </span>
            </div>
          </div>
        </div>

        {/* Contrast Warning or Pass Badge */}
        <div
          className={`p-2.5 rounded-lg border flex items-center justify-between ${
            wcagEvaluation.normalAa
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-amber-50 border-amber-200 text-amber-800'
          }`}
        >
          <div className="flex items-center gap-1.5">
            {wcagEvaluation.normalAa ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
            )}
            <div>
              <div className="font-bold text-[11px]">Contrast Ratio: {textContrast}:1</div>
              <div className="text-[10px] opacity-80">{wcagEvaluation.ratingText}</div>
            </div>
          </div>
        </div>
      </div>

      {/* 5. Headings, Bullets, and Dates */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 space-y-3">
        <div className="flex items-center space-x-1.5 font-bold uppercase text-[11px] text-slate-500 tracking-wider">
          <Sliders className="w-3.5 h-3.5 text-blue-600" />
          <span>Styles & Symbols</span>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Heading Style
            </label>
            <select
              value={style.headingStyle}
              onChange={(e) =>
                handleUpdate({ headingStyle: e.target.value as HeadingStyle })
              }
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white font-medium"
            >
              <option value="bar">Left Bar</option>
              <option value="underline">Underline</option>
              <option value="caps">All Caps Divider</option>
              <option value="boxed">Boxed Accent</option>
              <option value="pill">Pill Badge</option>
              <option value="plain">Plain</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Bullet Glyph
            </label>
            <select
              value={style.bulletStyle}
              onChange={(e) =>
                handleUpdate({ bulletStyle: e.target.value as BulletStyle })
              }
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white font-medium"
            >
              <option value="disc">Disc (•)</option>
              <option value="circle">Circle (◦)</option>
              <option value="square">Square (▪)</option>
              <option value="dash">Dash (–)</option>
              <option value="arrow">Arrow (➤)</option>
              <option value="none">None</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-[11px] font-semibold text-slate-600 mb-1">
            Date Format
          </label>
          <select
            value={style.dateFormat || 'MMM YYYY'}
            onChange={(e) => handleUpdate({ dateFormat: e.target.value })}
            className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white font-medium"
          >
            <option value="MMM YYYY">MMM YYYY (e.g., Jan 2024 - Present)</option>
            <option value="MM/YYYY">MM/YYYY (e.g., 01/2024 - Present)</option>
            <option value="YYYY">Year Only (e.g., 2021 - 2024)</option>
            <option value="Month YYYY">Full Month (e.g., January 2024)</option>
          </select>
        </div>
      </div>

      {/* 6. Margins & Spacings */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 space-y-3">
        <div className="flex items-center space-x-1.5 font-bold uppercase text-[11px] text-slate-500 tracking-wider">
          <Move className="w-3.5 h-3.5 text-blue-600" />
          <span>Margins & Spacing (pt)</span>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <span className="text-[11px] text-slate-500">Top: {style.margins.top}pt</span>
            <input
              type="range"
              min={16}
              max={60}
              step={2}
              value={style.margins.top}
              onChange={(e) => handleMarginsUpdate({ top: Number(e.target.value) })}
              className="w-full accent-blue-600"
            />
          </div>

          <div>
            <span className="text-[11px] text-slate-500">
              Bottom: {style.margins.bottom}pt
            </span>
            <input
              type="range"
              min={16}
              max={60}
              step={2}
              value={style.margins.bottom}
              onChange={(e) => handleMarginsUpdate({ bottom: Number(e.target.value) })}
              className="w-full accent-blue-600"
            />
          </div>

          <div>
            <span className="text-[11px] text-slate-500">Left: {style.margins.left}pt</span>
            <input
              type="range"
              min={20}
              max={64}
              step={2}
              value={style.margins.left}
              onChange={(e) => handleMarginsUpdate({ left: Number(e.target.value) })}
              className="w-full accent-blue-600"
            />
          </div>

          <div>
            <span className="text-[11px] text-slate-500">
              Right: {style.margins.right}pt
            </span>
            <input
              type="range"
              min={20}
              max={64}
              step={2}
              value={style.margins.right}
              onChange={(e) => handleMarginsUpdate({ right: Number(e.target.value) })}
              className="w-full accent-blue-600"
            />
          </div>
        </div>

        <div className="pt-2 border-t border-slate-100 space-y-2">
          <div>
            <div className="flex justify-between items-center mb-0.5">
              <span className="text-[11px] text-slate-500">
                Section Spacing: {style.spacing.sectionSpacing}pt
              </span>
            </div>
            <input
              type="range"
              min={6}
              max={28}
              step={1}
              value={style.spacing.sectionSpacing}
              onChange={(e) =>
                handleSpacingUpdate({ sectionSpacing: Number(e.target.value) })
              }
              className="w-full accent-blue-600"
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-0.5">
              <span className="text-[11px] text-slate-500">
                Item Spacing: {style.spacing.itemSpacing}pt
              </span>
            </div>
            <input
              type="range"
              min={3}
              max={18}
              step={1}
              value={style.spacing.itemSpacing}
              onChange={(e) =>
                handleSpacingUpdate({ itemSpacing: Number(e.target.value) })
              }
              className="w-full accent-blue-600"
            />
          </div>
        </div>
      </div>

      {/* Save Preset Modal */}
      {saveModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full p-5 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95">
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-blue-600" />
              <span>Save As My Template</span>
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              Store your current style tokens and palette as a reusable preset.
            </p>

            <div className="mt-4 space-y-3">
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Preset Name *
                </label>
                <input
                  type="text"
                  value={presetName}
                  onChange={(e) => setPresetName(e.target.value)}
                  placeholder="e.g. My Custom Executive"
                  className="w-full px-3 py-1.5 border border-slate-200 rounded-lg text-xs"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Description
                </label>
                <input
                  type="text"
                  value={presetDescription}
                  onChange={(e) => setPresetDescription(e.target.value)}
                  placeholder="Brief style summary"
                  className="w-full px-3 py-1.5 border border-slate-200 rounded-lg text-xs"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Category
                </label>
                <select
                  value={presetCategory}
                  onChange={(e) => setPresetCategory(e.target.value)}
                  className="w-full px-3 py-1.5 border border-slate-200 rounded-lg text-xs bg-white"
                >
                  <option value="single">Single Column</option>
                  <option value="sidebar">Sidebar</option>
                  <option value="creative">Creative</option>
                  <option value="minimal">Minimal</option>
                  <option value="academic">Academic</option>
                </select>
              </div>
            </div>

            <div className="mt-5 flex items-center justify-end space-x-2">
              <button
                type="button"
                onClick={() => setSaveModalOpen(false)}
                className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={!presetName.trim() || savingPreset}
                onClick={handleSaveUserPreset}
                className="px-4 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 disabled:opacity-50"
              >
                {savingPreset ? 'Saving...' : 'Save Preset'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

'use client';

import React from 'react';
import { useResume } from '@/context/ResumeContext';
import { TEMPLATE_PRESETS } from '@/lib/presets';
import { PageSize, BulletStyle, HeadingStyle, ColumnLayoutType } from '@/types/style';
import { Palette, Layout, Type, Move, Sliders } from 'lucide-react';

export const StylePanel: React.FC = () => {
  const { style, updateStyle, applyPreset } = useResume();

  const handleUpdate = (patch: Partial<typeof style>) => {
    updateStyle({
      ...style,
      ...patch,
    });
  };

  const handleTypographyUpdate = (patch: Partial<typeof style.typography>) => {
    updateStyle({
      ...style,
      typography: {
        ...style.typography,
        ...patch,
      },
    });
  };

  const handleFontSizesUpdate = (patch: Partial<typeof style.typography.fontSizes>) => {
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

  const handleSpacingUpdate = (patch: Partial<typeof style.spacing>) => {
    updateStyle({
      ...style,
      spacing: {
        ...style.spacing,
        ...patch,
      },
    });
  };

  const handleMarginsUpdate = (patch: Partial<typeof style.margins>) => {
    updateStyle({
      ...style,
      margins: {
        ...style.margins,
        ...patch,
      },
    });
  };

  const handleColorsUpdate = (patch: Partial<typeof style.colors>) => {
    updateStyle({
      ...style,
      colors: {
        ...style.colors,
        ...patch,
      },
    });
  };

  const handleLayoutUpdate = (patch: Partial<typeof style.layout>) => {
    updateStyle({
      ...style,
      layout: {
        ...style.layout,
        ...patch,
      },
    });
  };

  const colorPresets = [
    '#2563eb', // Royal Blue
    '#0f766e', // Deep Teal
    '#7c3aed', // Purple
    '#dc2626', // Crimson Red
    '#d97706', // Amber
    '#059669', // Emerald
    '#1e293b', // Slate Dark
  ];

  return (
    <div className="p-4 pb-20 overflow-y-auto max-h-full space-y-6 text-xs text-slate-700">
      {/* 1. Template Presets */}
      <div>
        <div className="flex items-center space-x-1.5 font-bold uppercase text-[11px] text-slate-500 tracking-wider mb-2.5">
          <Palette className="w-3.5 h-3.5 text-blue-600" />
          <span>Style Presets (Templates)</span>
        </div>
        <div className="grid grid-cols-1 gap-2">
          {TEMPLATE_PRESETS.map((preset) => {
            const isSelected = style.templateId === preset.id;
            return (
              <button
                key={preset.id}
                type="button"
                onClick={() => applyPreset(preset.style)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  isSelected
                    ? 'border-blue-600 bg-blue-50/50 shadow-sm ring-1 ring-blue-500'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <div className="font-bold text-slate-900 text-xs flex items-center justify-between">
                  <span>{preset.name}</span>
                  {isSelected && (
                    <span className="text-[10px] text-blue-600 font-semibold bg-blue-100 px-1.5 py-0.5 rounded">
                      Active
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-slate-500 mt-0.5">{preset.description}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. Layout & Page Dimensions */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 space-y-3">
        <div className="flex items-center space-x-1.5 font-bold uppercase text-[11px] text-slate-500 tracking-wider">
          <Layout className="w-3.5 h-3.5 text-blue-600" />
          <span>Layout & Format</span>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Page Size
            </label>
            <select
              value={style.pageSize}
              onChange={(e) => handleUpdate({ pageSize: e.target.value as PageSize })}
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white"
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
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white"
            >
              <option value="single">Single Column</option>
              <option value="sidebar_left">Sidebar on Left</option>
              <option value="sidebar_right">Sidebar on Right</option>
            </select>
          </div>
        </div>

        {style.layout.type !== 'single' && (
          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-[11px] font-semibold text-slate-600">
                Sidebar Width: {style.layout.sidebarWidthPercent}%
              </label>
            </div>
            <input
              type="range"
              min={25}
              max={45}
              step={1}
              value={style.layout.sidebarWidthPercent}
              onChange={(e) =>
                handleLayoutUpdate({ sidebarWidthPercent: Number(e.target.value) })
              }
              className="w-full accent-blue-600"
            />
          </div>
        )}
      </div>

      {/* 3. Typography */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 space-y-3">
        <div className="flex items-center space-x-1.5 font-bold uppercase text-[11px] text-slate-500 tracking-wider">
          <Type className="w-3.5 h-3.5 text-blue-600" />
          <span>Typography & Fonts</span>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Base Font
            </label>
            <select
              value={style.typography.baseFontFamily}
              onChange={(e) => handleTypographyUpdate({ baseFontFamily: e.target.value })}
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white"
            >
              <option value="Inter">Inter (Sans-serif)</option>
              <option value="Roboto">Roboto (Clean Sans)</option>
              <option value="Merriweather">Merriweather (Serif)</option>
              <option value="Cinzel">Cinzel (Classical)</option>
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
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white"
            >
              <option value="Inter">Inter (Sans-serif)</option>
              <option value="Roboto">Roboto (Clean Sans)</option>
              <option value="Merriweather">Merriweather (Serif)</option>
              <option value="Cinzel">Cinzel (Classical)</option>
            </select>
          </div>
        </div>

        {/* Font Sizes */}
        <div className="space-y-2 pt-1 border-t border-slate-100">
          <div>
            <div className="flex justify-between items-center mb-0.5">
              <span className="text-[11px] text-slate-500">Name Size</span>
              <span className="font-semibold text-slate-700">
                {style.typography.fontSizes.name}pt
              </span>
            </div>
            <input
              type="range"
              min={16}
              max={30}
              step={0.5}
              value={style.typography.fontSizes.name}
              onChange={(e) => handleFontSizesUpdate({ name: Number(e.target.value) })}
              className="w-full accent-blue-600"
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-0.5">
              <span className="text-[11px] text-slate-500">Section Headings</span>
              <span className="font-semibold text-slate-700">
                {style.typography.fontSizes.sectionHeading}pt
              </span>
            </div>
            <input
              type="range"
              min={10}
              max={18}
              step={0.5}
              value={style.typography.fontSizes.sectionHeading}
              onChange={(e) =>
                handleFontSizesUpdate({ sectionHeading: Number(e.target.value) })
              }
              className="w-full accent-blue-600"
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-0.5">
              <span className="text-[11px] text-slate-500">Body Text</span>
              <span className="font-semibold text-slate-700">
                {style.typography.fontSizes.body}pt
              </span>
            </div>
            <input
              type="range"
              min={8}
              max={12}
              step={0.5}
              value={style.typography.fontSizes.body}
              onChange={(e) => handleFontSizesUpdate({ body: Number(e.target.value) })}
              className="w-full accent-blue-600"
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-0.5">
              <span className="text-[11px] text-slate-500">Line Height</span>
              <span className="font-semibold text-slate-700">
                {style.typography.lineHeight}
              </span>
            </div>
            <input
              type="range"
              min={1.2}
              max={1.8}
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

      {/* 4. Colors */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 space-y-3">
        <div className="flex items-center space-x-1.5 font-bold uppercase text-[11px] text-slate-500 tracking-wider">
          <Palette className="w-3.5 h-3.5 text-blue-600" />
          <span>Colors & Palette</span>
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
            {/* Quick swatches */}
            <div className="flex items-center space-x-1 ml-auto">
              {colorPresets.map((c) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => handleColorsUpdate({ accent: c })}
                  style={{ backgroundColor: c }}
                  className="w-5 h-5 rounded-full ring-1 ring-slate-200 hover:scale-110 transition-transform"
                />
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Heading Style
            </label>
            <select
              value={style.headingStyle}
              onChange={(e) =>
                handleUpdate({ headingStyle: e.target.value as HeadingStyle })
              }
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white"
            >
              <option value="bar">Left Bar</option>
              <option value="underline">Underline</option>
              <option value="caps">All Caps Divider</option>
              <option value="plain">Plain</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Bullet Style
            </label>
            <select
              value={style.bulletStyle}
              onChange={(e) =>
                handleUpdate({ bulletStyle: e.target.value as BulletStyle })
              }
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white"
            >
              <option value="disc">Disc (•)</option>
              <option value="circle">Circle (◦)</option>
              <option value="square">Square (▪)</option>
              <option value="dash">Dash (–)</option>
              <option value="none">None</option>
            </select>
          </div>
        </div>
      </div>

      {/* 5. Margins & Spacing */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 space-y-3">
        <div className="flex items-center space-x-1.5 font-bold uppercase text-[11px] text-slate-500 tracking-wider">
          <Move className="w-3.5 h-3.5 text-blue-600" />
          <span>Margins & Spacing (pt)</span>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <span className="text-[11px] text-slate-500">Top Margin: {style.margins.top}pt</span>
            <input
              type="range"
              min={20}
              max={60}
              step={2}
              value={style.margins.top}
              onChange={(e) => handleMarginsUpdate({ top: Number(e.target.value) })}
              className="w-full accent-blue-600"
            />
          </div>

          <div>
            <span className="text-[11px] text-slate-500">Bottom: {style.margins.bottom}pt</span>
            <input
              type="range"
              min={20}
              max={60}
              step={2}
              value={style.margins.bottom}
              onChange={(e) => handleMarginsUpdate({ bottom: Number(e.target.value) })}
              className="w-full accent-blue-600"
            />
          </div>

          <div>
            <span className="text-[11px] text-slate-500">Left Margin: {style.margins.left}pt</span>
            <input
              type="range"
              min={24}
              max={64}
              step={2}
              value={style.margins.left}
              onChange={(e) => handleMarginsUpdate({ left: Number(e.target.value) })}
              className="w-full accent-blue-600"
            />
          </div>

          <div>
            <span className="text-[11px] text-slate-500">Right: {style.margins.right}pt</span>
            <input
              type="range"
              min={24}
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
              <span className="text-[11px] text-slate-500">Section Spacing</span>
              <span className="font-semibold text-slate-700">
                {style.spacing.sectionSpacing}pt
              </span>
            </div>
            <input
              type="range"
              min={8}
              max={24}
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
              <span className="text-[11px] text-slate-500">Item Spacing</span>
              <span className="font-semibold text-slate-700">
                {style.spacing.itemSpacing}pt
              </span>
            </div>
            <input
              type="range"
              min={4}
              max={16}
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
    </div>
  );
};

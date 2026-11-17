'use client';

import React from 'react';
import { useResume } from '@/context/ResumeContext';
import { Layout, Columns, MoveHorizontal, Sliders } from 'lucide-react';
import { ColumnLayoutType } from '@/types/style';

export const LayoutCard: React.FC = () => {
  const { style, content, updateStyle } = useResume();

  const layoutType = style.layout.type;
  const isTwoColumn = layoutType === 'sidebar_left' || layoutType === 'sidebar_right';
  const isMixLayout = layoutType === 'mix';
  const hasSidebar = isTwoColumn || isMixLayout;

  const currentWidthPercent = style.layout.sidebarWidthPercent || 32;

  const handleLayoutTypeChange = (type: ColumnLayoutType) => {
    updateStyle({
      ...style,
      layout: {
        ...style.layout,
        type,
      },
    });
  };

  const handleWidthChange = (width: number) => {
    updateStyle({
      ...style,
      layout: {
        ...style.layout,
        sidebarWidthPercent: width,
      },
    });
  };

  const handleSectionPlacement = (sectionId: string, placement: 'main' | 'sidebar' | 'full') => {
    const existingPlacement = { ...(style.layout.sectionPlacement || {}) };
    existingPlacement[sectionId] = placement;

    // Synchronize sidebarSectionIds & mainSectionIds
    let sidebarIds = style.layout.sidebarSectionIds.filter((id) => id !== sectionId);
    let mainIds = style.layout.mainSectionIds.filter((id) => id !== sectionId);

    if (placement === 'sidebar') {
      sidebarIds.push(sectionId);
    } else {
      mainIds.push(sectionId);
    }

    updateStyle({
      ...style,
      layout: {
        ...style.layout,
        sidebarSectionIds: sidebarIds,
        mainSectionIds: mainIds,
        sectionPlacement: existingPlacement,
      },
    });
  };

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-5">
      <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
        <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
          <Columns className="w-4 h-4" />
        </div>
        <div>
          <h3 className="font-bold text-sm text-slate-900">Columns & Layout</h3>
          <p className="text-xs text-slate-500">Column structure, sidebar width, and per-section placement</p>
        </div>
      </div>

      {/* 1. Layout Structure Buttons */}
      <div className="space-y-2">
        <label className="text-xs font-semibold text-slate-700">Layout Structure</label>
        <div className="grid grid-cols-2 gap-2">
          {[
            { id: 'single', label: '1 Column', desc: 'Standard single column' },
            { id: 'sidebar_left', label: 'Sidebar Left', desc: '2 Columns (Sidebar Left)' },
            { id: 'sidebar_right', label: 'Sidebar Right', desc: '2 Columns (Sidebar Right)' },
            { id: 'mix', label: 'Mix Layout', desc: 'Full-width header + 2 col body' },
          ].map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => handleLayoutTypeChange(item.id as ColumnLayoutType)}
              className={`p-3 rounded-xl border text-left transition-all ${
                layoutType === item.id
                  ? 'border-indigo-600 bg-indigo-50/50 text-indigo-900 font-bold shadow-xs'
                  : 'border-slate-200 hover:border-slate-300 text-slate-700'
              }`}
            >
              <div className="text-xs font-bold">{item.label}</div>
              <div className="text-[10px] text-slate-400 mt-0.5">{item.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* 2. Sidebar Width Slider */}
      {hasSidebar && (
        <div className="space-y-2 p-3 bg-slate-50 rounded-xl border border-slate-100">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-700 flex items-center gap-1.5">
              <MoveHorizontal className="w-3.5 h-3.5 text-slate-400" /> Sidebar Width
            </span>
            <span className="font-mono font-bold text-indigo-600 bg-white px-2 py-0.5 rounded border border-slate-200">
              {currentWidthPercent}%
            </span>
          </div>
          <input
            type="range"
            min={24}
            max={45}
            step={1}
            value={currentWidthPercent}
            onChange={(e) => handleWidthChange(Number(e.target.value))}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
          />
          <div className="flex justify-between text-[10px] text-slate-400 font-mono">
            <span>24% (Narrow)</span>
            <span>32% (Default)</span>
            <span>45% (Wide)</span>
          </div>
        </div>
      )}

      {/* 3. Section Placement Targeting */}
      {hasSidebar && content.sections && content.sections.length > 0 && (
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-700">Section Placement</label>
          <div className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
            {content.sections.map((sec) => {
              const currentPlacement =
                style.layout.sectionPlacement?.[sec.id] ||
                (style.layout.sidebarSectionIds.includes(sec.id)
                  ? 'sidebar'
                  : isMixLayout && sec.type === 'summary'
                  ? 'full'
                  : 'main');

              return (
                <div
                  key={sec.id}
                  className="flex items-center justify-between p-2 rounded-xl border border-slate-200 bg-white text-xs"
                >
                  <span className="font-medium text-slate-800 truncate max-w-[130px]">
                    {sec.title || sec.type}
                  </span>
                  <div className="flex items-center gap-1">
                    <button
                      type="button"
                      onClick={() => handleSectionPlacement(sec.id, 'main')}
                      className={`px-2 py-1 rounded-md text-[10px] font-semibold transition-colors ${
                        currentPlacement === 'main'
                          ? 'bg-indigo-600 text-white'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                      }`}
                    >
                      Main
                    </button>
                    <button
                      type="button"
                      onClick={() => handleSectionPlacement(sec.id, 'sidebar')}
                      className={`px-2 py-1 rounded-md text-[10px] font-semibold transition-colors ${
                        currentPlacement === 'sidebar'
                          ? 'bg-indigo-600 text-white'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                      }`}
                    >
                      Sidebar
                    </button>
                    {isMixLayout && (
                      <button
                        type="button"
                        onClick={() => handleSectionPlacement(sec.id, 'full')}
                        className={`px-2 py-1 rounded-md text-[10px] font-semibold transition-colors ${
                          currentPlacement === 'full'
                            ? 'bg-indigo-600 text-white'
                            : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                        }`}
                      >
                        Full
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

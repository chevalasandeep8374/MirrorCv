'use client';

import React from 'react';
import { useResume } from '@/context/ResumeContext';
import { AlignLeft, Calendar, Split } from 'lucide-react';
import { EntryLayoutConfig } from '@/types/style';

export const EntryLayoutCard: React.FC = () => {
  const { style, updateStyle } = useResume();

  const entryLayout = style.entryLayout || {
    structure: 'full_width',
    dateLocationPosition: 'right',
    headerSplitRatio: 'auto',
  };

  const handleUpdate = (patch: Partial<EntryLayoutConfig>) => {
    updateStyle({
      ...style,
      entryLayout: {
        ...entryLayout,
        ...patch,
      },
    });
  };

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-5">
      <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
        <div className="p-2 bg-sky-50 text-sky-600 rounded-xl">
          <AlignLeft className="w-4 h-4" />
        </div>
        <div>
          <h3 className="font-bold text-sm text-slate-900">Entry Header Layout</h3>
          <p className="text-xs text-slate-500">Date/location alignment and header column proportions</p>
        </div>
      </div>

      {/* 1. Date & Location Position */}
      <div className="space-y-2">
        <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
          <Calendar className="w-3.5 h-3.5 text-slate-400" /> Date & Location Position
        </label>
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => handleUpdate({ dateLocationPosition: 'right' })}
            className={`p-3 rounded-xl border text-left transition-all ${
              entryLayout.dateLocationPosition !== 'below_title'
                ? 'border-sky-600 bg-sky-50/50 text-sky-900 font-bold shadow-xs'
                : 'border-slate-200 hover:border-slate-300 text-slate-700'
            }`}
          >
            <div className="text-xs font-bold">Right Aligned</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Beside role title (Standard)</div>
          </button>
          <button
            type="button"
            onClick={() => handleUpdate({ dateLocationPosition: 'below_title' })}
            className={`p-3 rounded-xl border text-left transition-all ${
              entryLayout.dateLocationPosition === 'below_title'
                ? 'border-sky-600 bg-sky-50/50 text-sky-900 font-bold shadow-xs'
                : 'border-slate-200 hover:border-slate-300 text-slate-700'
            }`}
          >
            <div className="text-xs font-bold">Below Title</div>
            <div className="text-[10px] text-slate-400 mt-0.5">On second metadata line</div>
          </button>
        </div>
      </div>

      {/* 2. Split Ratio */}
      <div className="space-y-2">
        <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
          <Split className="w-3.5 h-3.5 text-slate-400" /> Header Split Ratio
        </label>
        <div className="grid grid-cols-3 gap-2">
          {[
            { id: 'auto', label: 'Auto (Fluid)' },
            { id: '50/50', label: '50 / 50' },
            { id: '70/30', label: '70 / 30' },
          ].map((r) => (
            <button
              key={r.id}
              type="button"
              onClick={() => handleUpdate({ headerSplitRatio: r.id as any })}
              className={`py-2 px-2.5 rounded-xl border text-center text-xs font-medium transition-all ${
                entryLayout.headerSplitRatio === r.id
                  ? 'border-sky-600 bg-sky-50/50 text-sky-900 font-bold shadow-xs'
                  : 'border-slate-200 hover:border-slate-300 text-slate-700'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

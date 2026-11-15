'use client';

import React from 'react';
import { ResumeStyle } from '@/types/style';
import { defaultResumeContent } from '@/lib/presets';
import { ResumeDocument } from '@/components/resume-renderer/ResumeDocument';
import { Check, Sparkles, Trash2 } from 'lucide-react';

interface TemplateCardProps {
  id: string;
  name: string;
  category: string;
  description: string;
  style: ResumeStyle;
  isActive?: boolean;
  isUserPreset?: boolean;
  onSelect: (style: ResumeStyle) => void;
  onDelete?: (id: string) => void;
}

export const TemplateCard: React.FC<TemplateCardProps> = ({
  id,
  name,
  category,
  description,
  style,
  isActive = false,
  isUserPreset = false,
  onSelect,
  onDelete,
}) => {
  return (
    <div
      onClick={() => onSelect(style)}
      className={`group relative rounded-2xl border bg-white p-3.5 transition-all cursor-pointer flex flex-col justify-between hover:shadow-lg ${
        isActive
          ? 'border-blue-600 ring-2 ring-blue-500/20 shadow-md'
          : 'border-slate-200 hover:border-slate-300'
      }`}
    >
      {/* Live Scaled Preview Thumbnail */}
      <div className="relative w-full h-64 bg-slate-100 rounded-xl overflow-hidden border border-slate-200 shadow-inner flex items-start justify-center pt-2">
        <div
          className="pointer-events-none select-none origin-top transition-transform group-hover:scale-[0.27]"
          style={{
            transform: 'scale(0.25)',
            width: '794px', // Standard A4 width in px at 96 DPI
            minHeight: '1123px',
          }}
        >
          <ResumeDocument content={defaultResumeContent} style={style} />
        </div>

        {/* Active Badge */}
        {isActive && (
          <div className="absolute top-3 right-3 bg-blue-600 text-white text-[11px] font-bold px-2.5 py-1 rounded-full shadow flex items-center gap-1 z-10">
            <Check className="w-3 h-3 stroke-[3]" />
            <span>Active</span>
          </div>
        )}

        {/* Custom Preset Badge */}
        {isUserPreset && (
          <div className="absolute top-3 left-3 bg-amber-500 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow flex items-center gap-1 z-10">
            <Sparkles className="w-2.5 h-2.5" />
            <span>Custom</span>
          </div>
        )}
      </div>

      {/* Info & Metadata */}
      <div className="mt-3.5 flex flex-col flex-1 justify-between">
        <div>
          <div className="flex items-center justify-between gap-2">
            <h3 className="font-bold text-slate-900 text-sm">{name}</h3>
            <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full shrink-0">
              {category}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1 line-clamp-2 leading-relaxed">
            {description}
          </p>
        </div>

        <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onSelect(style);
            }}
            className={`w-full py-1.5 px-3 rounded-lg text-xs font-semibold transition-all ${
              isActive
                ? 'bg-blue-50 text-blue-700 font-bold border border-blue-200'
                : 'bg-slate-900 text-white hover:bg-slate-800 shadow-xs'
            }`}
          >
            {isActive ? 'Currently In Use' : 'Apply Preset'}
          </button>

          {isUserPreset && onDelete && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                if (confirm(`Delete preset "${name}"?`)) {
                  onDelete(id);
                }
              }}
              className="ml-2 p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="Delete custom preset"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

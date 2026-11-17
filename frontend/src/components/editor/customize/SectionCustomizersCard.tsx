'use client';

import React from 'react';
import { useResume } from '@/context/ResumeContext';
import { Sparkles, Briefcase, List, CheckSquare } from 'lucide-react';
import { BulletStyle, SectionCustomizations } from '@/types/style';

const BULLET_STYLES: { id: BulletStyle; label: string; char: string }[] = [
  { id: 'disc', label: 'Disc', char: '•' },
  { id: 'circle', label: 'Circle', char: '◦' },
  { id: 'square', label: 'Square', char: '▪' },
  { id: 'dash', label: 'Dash', char: '–' },
  { id: 'arrow', label: 'Arrow', char: '➤' },
  { id: 'none', label: 'None', char: ' ' },
];

export const SectionCustomizersCard: React.FC = () => {
  const { style, updateStyle } = useResume();

  const secCust = style.sectionCustomizations || {};
  const currentSkillsStyle = secCust.skills?.style || 'compact';
  const currentExpOrder = secCust.experience?.titleSubtitleOrder || 'title_first';
  const currentBulletStyle = style.bulletStyle || 'disc';
  const groupPromotions = secCust.experience?.groupPromotions ?? true;

  const handleSkillsStyleChange = (val: 'grid' | 'rows' | 'compact' | 'bubble' | 'level') => {
    updateStyle({
      ...style,
      sectionCustomizations: {
        ...secCust,
        skills: {
          ...(secCust.skills || {}),
          style: val,
        },
      },
    });
  };

  const handleExpOrderChange = (val: 'title_first' | 'subtitle_first') => {
    updateStyle({
      ...style,
      sectionCustomizations: {
        ...secCust,
        experience: {
          ...(secCust.experience || {}),
          titleSubtitleOrder: val,
        },
        education: {
          ...(secCust.education || {}),
          titleSubtitleOrder: val,
        },
      },
    });
  };

  const handleToggleGroupPromotions = (enabled: boolean) => {
    updateStyle({
      ...style,
      sectionCustomizations: {
        ...secCust,
        experience: {
          ...(secCust.experience || {}),
          groupPromotions: enabled,
        },
      },
    });
  };

  const handleBulletStyleChange = (b: BulletStyle) => {
    updateStyle({
      ...style,
      bulletStyle: b,
    });
  };

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-5">
      <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
        <div className="p-2 bg-violet-50 text-violet-600 rounded-xl">
          <Sparkles className="w-4 h-4" />
        </div>
        <div>
          <h3 className="font-bold text-sm text-slate-900">Section-Specific Styling</h3>
          <p className="text-xs text-slate-500">Skills badge modes, title display order, and list markers</p>
        </div>
      </div>

      {/* 1. Skills Display Mode */}
      <div className="space-y-2">
        <label className="text-xs font-semibold text-slate-700">Skills & Badges Presentation</label>
        <div className="grid grid-cols-2 gap-2">
          {[
            { id: 'compact', label: 'Compact Chips', desc: 'Standard boxed badges' },
            { id: 'bubble', label: 'Bubble Pills', desc: 'Rounded pill shape with accent border' },
            { id: 'grid', label: 'Grid Columns', desc: '2 or 3-column aligned grid' },
            { id: 'level', label: 'Proficiency Dots', desc: '1-5 dots indicating skill level' },
          ].map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => handleSkillsStyleChange(item.id as any)}
              className={`p-3 rounded-xl border text-left transition-all ${
                currentSkillsStyle === item.id
                  ? 'border-violet-600 bg-violet-50/50 text-violet-950 font-bold shadow-xs'
                  : 'border-slate-200 hover:border-slate-300 text-slate-700'
              }`}
            >
              <div className="text-xs font-bold">{item.label}</div>
              <div className="text-[10px] text-slate-400 mt-0.5">{item.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* 2. Experience & Education Order */}
      <div className="space-y-2 pt-2 border-t border-slate-100">
        <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
          <Briefcase className="w-3.5 h-3.5 text-slate-400" /> Title & Subtitle Display Order
        </label>
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => handleExpOrderChange('title_first')}
            className={`p-2.5 rounded-xl border text-left text-xs transition-all ${
              currentExpOrder === 'title_first'
                ? 'border-violet-600 bg-violet-50/50 text-violet-900 font-bold shadow-xs'
                : 'border-slate-200 text-slate-700'
            }`}
          >
            <div className="font-bold">Title First</div>
            <div className="text-[10px] text-slate-400">Senior Engineer | Acme Corp</div>
          </button>
          <button
            type="button"
            onClick={() => handleExpOrderChange('subtitle_first')}
            className={`p-2.5 rounded-xl border text-left text-xs transition-all ${
              currentExpOrder === 'subtitle_first'
                ? 'border-violet-600 bg-violet-50/50 text-violet-900 font-bold shadow-xs'
                : 'border-slate-200 text-slate-700'
            }`}
          >
            <div className="font-bold">Company First</div>
            <div className="text-[10px] text-slate-400">Acme Corp | Senior Engineer</div>
          </button>
        </div>
      </div>

      {/* 3. Promotion Grouping Toggle */}
      <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
        <div>
          <div className="text-xs font-semibold text-slate-800">Group Promotional Roles</div>
          <div className="text-[11px] text-slate-500">Stack sequential promotions under one company header</div>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            aria-label="Group Promotional Roles"
            checked={groupPromotions}
            onChange={(e) => handleToggleGroupPromotions(e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-slate-200 peer-focus:outline-hidden rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-violet-600"></div>
        </label>
      </div>

      {/* 4. List Bullet Marker Style */}
      <div className="space-y-2 pt-2 border-t border-slate-100">
        <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
          <List className="w-3.5 h-3.5 text-slate-400" /> List Bullet Markers
        </label>
        <div className="grid grid-cols-3 gap-2">
          {BULLET_STYLES.map((b) => (
            <button
              key={b.id}
              type="button"
              onClick={() => handleBulletStyleChange(b.id)}
              className={`py-2 px-2.5 rounded-xl border flex items-center justify-center gap-2 text-xs font-medium transition-all ${
                currentBulletStyle === b.id
                  ? 'border-violet-600 bg-violet-50/50 text-violet-900 font-bold shadow-xs'
                  : 'border-slate-200 text-slate-700'
              }`}
            >
              <span className="text-base text-violet-600">{b.char}</span>
              <span>{b.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

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
  const currentSkillsStyle = secCust.skills?.style || 'rows';
  const currentExpOrder = secCust.experience?.titleSubtitleOrder || 'title_first';
  const currentBulletStyle = style.bulletStyle || 'disc';
  const groupPromotions = secCust.experience?.groupPromotions ?? true;

  const handleSkillsStyleChange = (val: 'rows' | 'stacked' | 'compact' | 'bubble' | 'grid' | 'level') => {
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

  const handleSubInfoStyleChange = (sep: 'colon' | 'dash' | 'bracket') => {
    updateStyle({
      ...style,
      sectionCustomizations: {
        ...secCust,
        skills: {
          ...(secCust.skills || {}),
          subInfoStyle: sep,
        },
      },
    });
  };

  const handleToggleBullets = (enabled: boolean) => {
    updateStyle({
      ...style,
      sectionCustomizations: {
        ...secCust,
        skills: {
          ...(secCust.skills || {}),
          startRowsWithBullets: enabled,
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
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-slate-700">Skills Presentation</label>
          <span className="text-[10px] text-slate-400">Preview & PDF layout</span>
        </div>
        <div className="grid grid-cols-2 gap-2">
          {[
            { id: 'rows', label: 'Normal Text (Inline)', desc: 'Standard resume text: Category: Skills' },
            { id: 'stacked', label: 'Normal Text (Stacked)', desc: 'Category header with plain skills below' },
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
                (currentSkillsStyle === item.id || (item.id === 'rows' && currentSkillsStyle === 'normal'))
                  ? 'border-violet-600 bg-violet-50/50 text-violet-950 font-bold shadow-xs'
                  : 'border-slate-200 hover:border-slate-300 text-slate-700'
              }`}
            >
              <div className="text-xs font-bold">{item.label}</div>
              <div className="text-[10px] text-slate-400 mt-0.5">{item.desc}</div>
            </button>
          ))}
        </div>

        {/* Sub-controls when Normal Text (Inline) is active */}
        {(currentSkillsStyle === 'rows' || currentSkillsStyle === 'normal') && (
          <div className="p-3 bg-slate-50/80 rounded-xl border border-slate-200/80 space-y-2.5 mt-2">
            <div className="text-[11px] font-semibold text-slate-700">Normal Text Formatting Options</div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-600">Separator Style:</span>
              <div className="inline-flex rounded-lg border border-slate-200 bg-white p-0.5">
                {[
                  { id: 'colon', label: 'Colon ( : )' },
                  { id: 'dash', label: 'Dash ( – )' },
                  { id: 'bracket', label: 'Bracket ( ... )' },
                ].map((sep) => (
                  <button
                    key={sep.id}
                    type="button"
                    onClick={() => handleSubInfoStyleChange(sep.id as any)}
                    className={`px-2 py-0.5 text-[11px] rounded-md transition-all ${
                      (secCust.skills?.subInfoStyle || 'colon') === sep.id
                        ? 'bg-violet-600 text-white font-medium shadow-xs'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    {sep.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between text-xs pt-1.5 border-t border-slate-200/60">
              <span className="text-slate-600">Start rows with bullet ( • ):</span>
              <button
                type="button"
                onClick={() => handleToggleBullets(!secCust.skills?.startRowsWithBullets)}
                className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-hidden ${
                  secCust.skills?.startRowsWithBullets ? 'bg-violet-600' : 'bg-slate-200'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out ${
                    secCust.skills?.startRowsWithBullets ? 'translate-x-4' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
          </div>
        )}
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

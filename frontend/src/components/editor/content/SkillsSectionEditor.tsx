'use client';

import React, { useState } from 'react';
import { SectionItem, BulletItem } from '@/types/content';
import { Plus, X, Star, Tag, Sparkles } from 'lucide-react';

interface SkillsSectionEditorProps {
  item: SectionItem;
  onUpdate: (data: Partial<SectionItem>) => void;
  onAddBullet: () => void;
  onRemoveBullet: (bulletId: string) => void;
  onUpdateBullet: (bulletId: string, patch: Partial<BulletItem>) => void;
}

export const SkillsSectionEditor: React.FC<SkillsSectionEditorProps> = ({
  item,
  onUpdate,
  onAddBullet,
  onRemoveBullet,
  onUpdateBullet,
}) => {
  const [inputValue, setInputValue] = useState('');

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addSkillFromInput();
    }
  };

  const addSkillFromInput = () => {
    const trimmed = inputValue.trim().replace(/^,+|,+$/g, '');
    if (!trimmed) return;

    // Support comma-separated batch pasting
    const newSkillNames = trimmed
      .split(',')
      .map((s) => s.trim())
      .filter((s) => s.length > 0);

    const newBullets: BulletItem[] = [
      ...(item.bullets || []),
      ...newSkillNames.map((name) => ({
        id: `skill-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
        text: name,
        proficiency: null,
      })),
    ];

    onUpdate({ bullets: newBullets });
    setInputValue('');
  };

  const setProficiency = (bulletId: string, currentLevel: number | null | undefined, newLevel: number) => {
    // If clicking same level, toggle off to null
    const targetLevel = currentLevel === newLevel ? null : newLevel;
    onUpdateBullet(bulletId, { proficiency: targetLevel });
  };

  return (
    <div className="space-y-3">
      {/* Category / Group Title */}
      <div>
        <label className="block text-[11px] font-semibold text-slate-500 mb-1">
          Skill Group / Category Name
        </label>
        <input
          type="text"
          value={item.title || ''}
          onChange={(e) => onUpdate({ title: e.target.value })}
          placeholder="e.g. Languages & Frameworks, Cloud, Tools, or Core Competencies"
          className="w-full text-xs px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 font-medium"
        />
      </div>

      {/* Quick Add Skill Chips Input */}
      <div>
        <label className="block text-[11px] font-semibold text-slate-500 mb-1 flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <Tag className="w-3.5 h-3.5 text-blue-600" />
            <span>Skills in this group (Type & press Enter or comma)</span>
          </span>
          <span className="text-[10px] text-slate-400">{(item.bullets || []).length} skills</span>
        </label>
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type skill name and press Enter (e.g. TypeScript, React, Docker)..."
            className="flex-1 text-xs px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
          />
          <button
            type="button"
            onClick={addSkillFromInput}
            disabled={!inputValue.trim()}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white font-semibold text-xs rounded-lg transition-colors flex items-center gap-1"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add</span>
          </button>
        </div>
      </div>

      {/* Rendered Skill Chips with Level Dots */}
      <div className="flex flex-wrap gap-2 pt-1">
        {(item.bullets || []).map((bullet) => {
          const prof = bullet.proficiency;
          return (
            <div
              key={bullet.id}
              className="inline-flex items-center gap-1.5 bg-white border border-slate-200 hover:border-slate-300 rounded-xl px-2.5 py-1 text-xs shadow-2xs group transition-all"
            >
              <input
                type="text"
                value={bullet.text}
                onChange={(e) => onUpdateBullet(bullet.id, { text: e.target.value })}
                className="bg-transparent border-none outline-hidden font-medium text-slate-800 text-xs w-auto min-w-[3rem] focus:ring-0 p-0"
                style={{ width: `${Math.max(bullet.text.length, 3)}ch` }}
              />

              {/* 1-5 Proficiency Dots */}
              <div
                className="flex items-center gap-0.5 ml-1 pl-1.5 border-l border-slate-100"
                title="Proficiency level (1 to 5, optional)"
              >
                {[1, 2, 3, 4, 5].map((lvl) => (
                  <button
                    key={lvl}
                    type="button"
                    onClick={() => setProficiency(bullet.id, prof, lvl)}
                    className={`w-2 h-2 rounded-full transition-transform hover:scale-125 ${
                      prof != null && prof >= lvl
                        ? 'bg-blue-600'
                        : 'bg-slate-200 hover:bg-slate-300'
                    }`}
                  />
                ))}
              </div>

              {/* Remove Chip */}
              <button
                type="button"
                onClick={() => onRemoveBullet(bullet.id)}
                className="text-slate-400 hover:text-rose-500 transition-colors p-0.5 ml-0.5"
                title="Remove skill"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};

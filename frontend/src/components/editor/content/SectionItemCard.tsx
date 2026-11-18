'use client';

import React, { useState } from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { SectionItem, SectionType, ItemType, BulletItem, StructuredDates } from '@/types/content';
import { BulletList } from './BulletList';
import { StructuredDateEditor } from './StructuredDateEditor';
import { SkillsSectionEditor } from './SkillsSectionEditor';
import {
  GripVertical,
  Trash2,
  Copy,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronRight,
  GitBranch,
  Link as LinkIcon,
} from 'lucide-react';

interface SectionItemCardProps {
  item: SectionItem;
  sectionType: SectionType;
  onUpdate: (itemData: Partial<SectionItem>) => void;
  onRemove: () => void;
  onDuplicate?: () => void;
  onAddBullet: () => void;
  onRemoveBullet: (bulletId: string) => void;
  onUpdateBullet: (bulletId: string, patch: string | Partial<BulletItem>) => void;
  onReorderBullets: (oldIndex: number, newIndex: number) => void;
}

export const SectionItemCard: React.FC<SectionItemCardProps> = ({
  item,
  sectionType,
  onUpdate,
  onRemove,
  onDuplicate,
  onAddBullet,
  onRemoveBullet,
  onUpdateBullet,
  onReorderBullets,
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: item.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  };

  const isHidden = item.visible === false;

  // Dynamic placeholders based on section type
  const getPlaceholders = () => {
    switch (sectionType) {
      case 'experience':
        return {
          title: 'Job Title (e.g. Principal Software Engineer)',
          subtitle: 'Company / Employer (e.g. Acme Cloud Systems)',
          dateRange: '2021 – Present',
          location: 'San Francisco, CA',
        };
      case 'education':
        return {
          title: 'Degree / Major (e.g. B.S. in Computer Science)',
          subtitle: 'University / Institution (e.g. UC Berkeley)',
          dateRange: '2016 – 2020',
          location: 'Berkeley, CA',
        };
      case 'projects':
        return {
          title: 'Project Name (e.g. DocMorph Engine)',
          subtitle: 'Role / Tech Stack (e.g. Creator / Rust & Next.js)',
          dateRange: '2023 – 2024',
          location: 'github.com/example',
        };
      case 'skills':
        return {
          title: 'Skill Group (e.g. Languages & Frameworks)',
          subtitle: 'Level / Focus (optional)',
          dateRange: '',
          location: '',
        };
      case 'certifications':
        return {
          title: 'Certification Name (e.g. AWS Solutions Architect Professional)',
          subtitle: 'Issuing Organization (e.g. Amazon Web Services)',
          dateRange: '2023',
          location: '',
        };
      case 'languages':
        return {
          title: 'Language (e.g. English, French, Hindi)',
          subtitle: 'Proficiency Level (e.g. Native, Fluent, C1, Conversational)',
          dateRange: '',
          location: '',
        };
      case 'awards':
        return {
          title: 'Award / Honor Name',
          subtitle: 'Granting Organization / Contest',
          dateRange: 'Year',
          location: '',
        };
      case 'volunteering':
        return {
          title: 'Volunteer Role / Position',
          subtitle: 'Organization / Cause',
          dateRange: 'Timeframe',
          location: 'City, Country',
        };
      case 'interests':
        return {
          title: 'Interest Category / Activity',
          subtitle: 'Details / Specialization',
          dateRange: '',
          location: '',
        };
      default:
        return {
          title: 'Title / Role',
          subtitle: 'Organization / Issuer',
          dateRange: 'Date',
          location: 'Location',
        };
    }
  };

  const placeholders = getPlaceholders();

  // Summary headline for collapsed view
  const summaryTitle = item.title || item.subtitle || 'Untitled Item';
  const summarySubtitle = item.subtitle ? ` • ${item.subtitle}` : '';
  const summaryDate = item.dateRange ? ` (${item.dateRange})` : '';

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`border rounded-xl p-3 shadow-2xs mb-2.5 group/item transition-all ${
        isHidden
          ? 'bg-slate-50 border-dashed border-amber-300 opacity-60'
          : 'bg-white border-slate-200/90 hover:border-slate-300'
      }`}
    >
      {/* Top Bar with Drag Handle, Summary, Collapse, Duplicate, Eye, and Delete */}
      <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100 select-none">
        <div className="flex items-center space-x-2 flex-1 min-w-0">
          <button
            type="button"
            {...attributes}
            {...listeners}
            className="p-1 text-slate-300 hover:text-slate-600 cursor-grab active:cursor-grabbing shrink-0"
            title="Drag to reorder item"
          >
            <GripVertical className="w-4 h-4" />
          </button>

          <button
            type="button"
            onClick={() => setIsExpanded((prev) => !prev)}
            className="p-0.5 text-slate-400 hover:text-slate-700 transition-colors"
          >
            {isExpanded ? (
              <ChevronDown className="w-3.5 h-3.5" />
            ) : (
              <ChevronRight className="w-3.5 h-3.5" />
            )}
          </button>

          <span
            onClick={() => setIsExpanded((prev) => !prev)}
            className="text-xs font-bold text-slate-800 truncate cursor-pointer hover:text-blue-600 transition-colors"
          >
            {summaryTitle}
            <span className="font-normal text-slate-500">{summarySubtitle}{summaryDate}</span>
          </span>

          {item.groupId && (
            <span className="text-[9px] bg-indigo-50 text-indigo-700 border border-indigo-200/60 px-1.5 py-0.5 rounded-full font-bold shrink-0 flex items-center gap-0.5">
              <GitBranch className="w-2.5 h-2.5" />
              <span>Promoted Group</span>
            </span>
          )}

          {isHidden && (
            <span className="text-[10px] bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded font-bold shrink-0">
              Hidden
            </span>
          )}
        </div>

        <div className="flex items-center space-x-1 shrink-0">
          {/* Per-item visibility toggle */}
          <button
            type="button"
            onClick={() => onUpdate({ visible: isHidden ? true : false })}
            className={`p-1 rounded transition-colors ${
              isHidden
                ? 'text-amber-600 bg-amber-50 hover:bg-amber-100'
                : 'text-slate-400 hover:text-slate-700'
            }`}
            title={isHidden ? 'Click to show item on resume' : 'Hide this item on current version'}
          >
            {isHidden ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
          </button>

          {/* Duplicate Item */}
          {onDuplicate && (
            <button
              type="button"
              onClick={onDuplicate}
              className="p-1 text-slate-400 hover:text-blue-600 transition-colors"
              title="Duplicate entry"
            >
              <Copy className="w-3.5 h-3.5" />
            </button>
          )}

          {/* Delete item */}
          <button
            type="button"
            onClick={onRemove}
            className="p-1 text-slate-400 hover:text-rose-600 transition-colors"
            title="Delete item"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Expanded Item Body */}
      {isExpanded && (
        <div className="space-y-3 pt-1">
          {/* Skills Specific Editor */}
          {sectionType === 'skills' ? (
            <SkillsSectionEditor
              item={item}
              onUpdate={onUpdate}
              onAddBullet={onAddBullet}
              onRemoveBullet={onRemoveBullet}
              onUpdateBullet={(bId, patch) => onUpdateBullet(bId, patch)}
            />
          ) : (
            <>
              {/* Standard Item Form Inputs */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 text-xs">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                    Title / Role / Degree
                  </label>
                  <input
                    type="text"
                    value={item.title || ''}
                    onChange={(e) => onUpdate({ title: e.target.value })}
                    placeholder={placeholders.title}
                    className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 bg-white"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                    Organization / Company
                  </label>
                  <input
                    type="text"
                    value={item.subtitle || ''}
                    onChange={(e) => onUpdate({ subtitle: e.target.value })}
                    placeholder={placeholders.subtitle}
                    className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 bg-white"
                  />
                </div>

                {/* Location */}
                {sectionType !== 'certifications' && sectionType !== 'languages' && (
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                      Location
                    </label>
                    <input
                      type="text"
                      value={item.location || ''}
                      onChange={(e) => onUpdate({ location: e.target.value })}
                      placeholder={placeholders.location}
                      className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 bg-white"
                    />
                  </div>
                )}

                {/* Optional Item External Link */}
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1 flex items-center gap-1">
                    <LinkIcon className="w-3 h-3 text-slate-400" />
                    <span>Project or Org Link (Optional)</span>
                  </label>
                  <input
                    type="text"
                    value={item.link?.url || ''}
                    onChange={(e) =>
                      onUpdate({
                        link: e.target.value ? { url: e.target.value, label: item.link?.label || 'Link' } : null,
                      })
                    }
                    placeholder="https://github.com/... or https://..."
                    className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 bg-white"
                  />
                </div>
              </div>

              {/* Structured Date Editor */}
              {sectionType !== 'languages' && (
                <div className="pt-1">
                  <StructuredDateEditor
                    dates={item.dates}
                    dateRange={item.dateRange || ''}
                    onChange={(newDates, newDateRange) =>
                      onUpdate({
                        dates: newDates,
                        dateRange: newDateRange,
                      })
                    }
                  />
                </div>
              )}

              {/* Promotion / Consecutive Role Grouping */}
              {sectionType === 'experience' && (
                <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <GitBranch className="w-3.5 h-3.5 text-indigo-600" />
                    <div>
                      <span className="text-[11px] font-semibold text-slate-700">Group as Promotion</span>
                      <p className="text-[10px] text-slate-400">Combine multiple roles under the same company header</p>
                    </div>
                  </div>
                  <input
                    type="text"
                    value={item.groupId || ''}
                    onChange={(e) => onUpdate({ groupId: e.target.value || null })}
                    placeholder="Group ID (e.g. google-career)"
                    className="text-xs px-2 py-1 border border-slate-200 rounded-lg w-40 bg-white focus:outline-hidden focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
              )}

              {/* Layout format for custom sections */}
              {sectionType === 'custom' && (
                <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                  <label className="text-[11px] font-semibold text-slate-600">
                    Display Format
                  </label>
                  <select
                    value={item.itemType || 'list'}
                    onChange={(e) => onUpdate({ itemType: e.target.value as ItemType })}
                    className="text-xs px-2 py-1 border border-slate-200 rounded-lg bg-white"
                  >
                    <option value="list">Bullet List</option>
                    <option value="timeline">Timeline</option>
                    <option value="paragraph">Prose Paragraph</option>
                    <option value="tags">Badge Tags</option>
                  </select>
                </div>
              )}

              {/* Bullets List */}
              <BulletList
                bullets={item.bullets || []}
                onAddBullet={onAddBullet}
                onRemoveBullet={onRemoveBullet}
                onUpdateBullet={onUpdateBullet}
                onReorderBullets={onReorderBullets}
              />
            </>
          )}
        </div>
      )}
    </div>
  );
};

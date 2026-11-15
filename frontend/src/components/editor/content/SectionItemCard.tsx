'use client';

import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { SectionItem, SectionType, ItemType, BulletItem } from '@/types/content';
import { BulletList } from './BulletList';
import { GripVertical, Trash2, Eye, EyeOff } from 'lucide-react';

interface SectionItemCardProps {
  item: SectionItem;
  sectionType: SectionType;
  onUpdate: (itemData: Partial<SectionItem>) => void;
  onRemove: () => void;
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
  onAddBullet,
  onRemoveBullet,
  onUpdateBullet,
  onReorderBullets,
}) => {
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
          subtitle: 'Company (e.g. Acme Cloud Platforms)',
          dateRange: '2021 - Present',
          location: 'San Francisco, CA',
        };
      case 'education':
        return {
          title: 'Degree / Major (e.g. B.S. in Computer Science)',
          subtitle: 'Institution (e.g. UC Berkeley)',
          dateRange: '2012 - 2016',
          location: 'Berkeley, CA',
        };
      case 'projects':
        return {
          title: 'Project Title (e.g. DocMorph Engine)',
          subtitle: 'Role / Tech Stack (e.g. Creator / Next.js & Rust)',
          dateRange: '2023 - 2024',
          location: 'GitHub',
        };
      case 'skills':
        return {
          title: 'Skill Category (e.g. Frontend)',
          subtitle: 'Proficiency / Note (optional)',
          dateRange: '',
          location: '',
        };
      case 'certifications':
        return {
          title: 'Certification Name (e.g. AWS Solutions Architect)',
          subtitle: 'Issuing Organization (e.g. Amazon)',
          dateRange: '2023',
          location: '',
        };
      case 'languages':
        return {
          title: 'Language (e.g. English, French, Hindi)',
          subtitle: 'Proficiency Level (e.g. Native, Fluent, C1)',
          dateRange: '',
          location: '',
        };
      case 'awards':
        return {
          title: 'Award / Honor Name',
          subtitle: 'Grantor / Competition',
          dateRange: 'Year',
          location: '',
        };
      default:
        return {
          title: 'Title',
          subtitle: 'Subtitle / Organization',
          dateRange: 'Date',
          location: 'Location',
        };
    }
  };

  const placeholders = getPlaceholders();

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`border rounded-xl p-3 shadow-sm mb-3 group/item transition-all ${
        isHidden
          ? 'bg-slate-50 border-dashed border-amber-300 opacity-60'
          : 'bg-white border-slate-200 hover:border-slate-300'
      }`}
    >
      {/* Top Bar with Drag Handle, Visibility Toggle, and Delete */}
      <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100">
        <div className="flex items-center space-x-1.5 flex-1 min-w-0">
          <button
            type="button"
            {...attributes}
            {...listeners}
            className="p-1 text-slate-400 hover:text-slate-700 cursor-grab active:cursor-grabbing shrink-0"
            title="Drag to reorder item"
          >
            <GripVertical className="w-4 h-4" />
          </button>
          <span className="text-xs font-bold text-slate-800 truncate">
            {item.title || item.subtitle || 'Untitled Item'}
          </span>
          {isHidden && (
            <span className="text-[10px] bg-amber-100 text-amber-800 px-1.5 py-0.2 rounded font-medium shrink-0">
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

          <button
            type="button"
            onClick={onRemove}
            className="p-1 text-slate-300 hover:text-rose-500 transition-colors"
            title="Delete item"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Item Form Inputs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
        <div>
          <label className="block text-[11px] font-semibold text-slate-500 mb-0.5">
            Title
          </label>
          <input
            type="text"
            value={item.title || ''}
            onChange={(e) => onUpdate({ title: e.target.value })}
            placeholder={placeholders.title}
            className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-[11px] font-semibold text-slate-500 mb-0.5">
            Subtitle / Organization
          </label>
          <input
            type="text"
            value={item.subtitle || ''}
            onChange={(e) => onUpdate({ subtitle: e.target.value })}
            placeholder={placeholders.subtitle}
            className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        {sectionType !== 'skills' && sectionType !== 'languages' && (
          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-0.5">
              Date Range
            </label>
            <input
              type="text"
              value={item.dateRange || ''}
              onChange={(e) => onUpdate({ dateRange: e.target.value })}
              placeholder={placeholders.dateRange}
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        )}

        {sectionType !== 'skills' &&
          sectionType !== 'certifications' &&
          sectionType !== 'languages' && (
            <div>
              <label className="block text-[11px] font-semibold text-slate-500 mb-0.5">
                Location
              </label>
              <input
                type="text"
                value={item.location || ''}
                onChange={(e) => onUpdate({ location: e.target.value })}
                placeholder={placeholders.location}
                className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          )}
      </div>

      {/* Item Type selection for custom sections */}
      {sectionType === 'custom' && (
        <div className="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between">
          <label className="text-[11px] font-semibold text-slate-500">
            Layout Format
          </label>
          <select
            value={item.itemType || 'list'}
            onChange={(e) => onUpdate({ itemType: e.target.value as ItemType })}
            className="text-xs px-2 py-1 border border-slate-200 rounded bg-white"
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
    </div>
  );
};

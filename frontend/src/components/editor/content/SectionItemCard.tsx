'use client';

import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { SectionItem, SectionType } from '@/types/content';
import { BulletList } from './BulletList';
import { GripVertical, Trash2 } from 'lucide-react';

interface SectionItemCardProps {
  item: SectionItem;
  sectionType: SectionType;
  onUpdate: (itemData: Partial<SectionItem>) => void;
  onRemove: () => void;
  onAddBullet: () => void;
  onRemoveBullet: (bulletId: string) => void;
  onUpdateBullet: (bulletId: string, text: string) => void;
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
      className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm mb-3 group/item transition-shadow hover:border-slate-300"
    >
      {/* Top Bar with Drag Handle and Delete */}
      <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100">
        <div className="flex items-center space-x-1.5">
          <button
            type="button"
            {...attributes}
            {...listeners}
            className="p-1 text-slate-400 hover:text-slate-700 cursor-grab active:cursor-grabbing"
            title="Drag to reorder item"
          >
            <GripVertical className="w-4 h-4" />
          </button>
          <span className="text-xs font-bold text-slate-800 truncate max-w-[240px]">
            {item.title || item.subtitle || 'Untitled Item'}
          </span>
        </div>

        <button
          type="button"
          onClick={onRemove}
          className="p-1 text-slate-300 hover:text-rose-500 transition-colors"
          title="Delete item"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
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

        {sectionType !== 'skills' && (
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

        {sectionType !== 'skills' && sectionType !== 'certifications' && (
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

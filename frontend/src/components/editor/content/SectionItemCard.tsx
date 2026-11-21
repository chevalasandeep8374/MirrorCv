'use client';

import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { SectionItem, SectionType } from '@/types/content';
import {
  GripVertical,
  Trash2,
  Eye,
  EyeOff,
  ChevronRight,
  GitBranch,
} from 'lucide-react';

interface SectionItemCardProps {
  item: SectionItem;
  sectionType: SectionType;
  onEdit: () => void;
  onUpdate: (itemData: Partial<SectionItem>) => void;
  onRemove: () => void;
}

export const SectionItemCard: React.FC<SectionItemCardProps> = ({
  item,
  sectionType,
  onEdit,
  onUpdate,
  onRemove,
}) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: item.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  };

  const isHidden = item.visible === false;

  // Summary headline
  const summaryTitle = item.title || item.subtitle || (sectionType === 'skills' ? 'Untitled Skill' : 'Untitled Entry');
  const summarySubtitle = item.subtitle ? item.subtitle : '';
  const summaryDate = item.dateRange ? `(${item.dateRange})` : '';

  return (
    <div
      ref={setNodeRef}
      style={style}
      onClick={onEdit}
      className={`border rounded-xl p-3 mb-2 transition-all duration-150 cursor-pointer select-none group/item ${
        isHidden
          ? 'bg-slate-50 border-dashed border-amber-300 opacity-60'
          : 'bg-white border-slate-200/90 hover:border-slate-300 hover:shadow-xs hover:bg-slate-50/70'
      }`}
    >
      <div className="flex items-center justify-between">
        {/* Left Side: Grip Handle + Title / Subtitle / Badges */}
        <div className="flex items-center space-x-2.5 flex-1 min-w-0">
          <button
            type="button"
            {...attributes}
            {...listeners}
            onClick={(e) => e.stopPropagation()}
            className="p-1 -ml-0.5 text-slate-300 hover:text-slate-600 cursor-grab active:cursor-grabbing shrink-0 transition-colors"
            title="Drag to reorder entry"
          >
            <GripVertical className="w-4 h-4" />
          </button>

          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-[14px] sm:text-[15px] font-black text-black truncate group-hover/item:text-blue-600 transition-colors">
                {summaryTitle}
              </span>

              {item.groupId && (
                <span className="text-[9px] bg-indigo-50 text-indigo-700 border border-indigo-200/60 px-1.5 py-0.5 rounded-full font-bold shrink-0 flex items-center gap-0.5">
                  <GitBranch className="w-2.5 h-2.5" />
                  <span>Promoted</span>
                </span>
              )}

              {isHidden && (
                <span className="text-[10px] bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded font-bold shrink-0">
                  Hidden
                </span>
              )}
            </div>

            {(summarySubtitle || summaryDate) && (
              <p className="text-xs text-slate-700 font-medium truncate mt-0.5">
                {summarySubtitle}
                {summarySubtitle && summaryDate ? ' · ' : ''}
                {summaryDate}
              </p>
            )}
          </div>
        </div>

        {/* Right Action Buttons */}
        <div
          className="flex items-center space-x-1 shrink-0 ml-2"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Per-item visibility toggle */}
          <button
            type="button"
            onClick={() => onUpdate({ visible: isHidden ? true : false })}
            className={`p-2 rounded-lg transition-all active:scale-95 cursor-pointer ${
              isHidden
                ? 'text-amber-600 bg-amber-50 hover:bg-amber-100'
                : 'text-slate-500 hover:text-black hover:bg-slate-100'
            }`}
            title={isHidden ? 'Click to show entry on resume' : 'Hide this entry'}
          >
            {isHidden ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>

          {/* Delete item */}
          <button
            type="button"
            onClick={onRemove}
            className="p-2 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-all active:scale-95 cursor-pointer"
            title="Delete entry"
          >
            <Trash2 className="w-4 h-4" />
          </button>

          {/* Chevron Right (Edit entry navigation) */}
          <button
            type="button"
            onClick={onEdit}
            className="p-2 text-slate-500 group-hover/item:text-black hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
            title="Edit entry"
          >
            <ChevronRight className="w-4.5 h-4.5" />
          </button>
        </div>
      </div>
    </div>
  );
};

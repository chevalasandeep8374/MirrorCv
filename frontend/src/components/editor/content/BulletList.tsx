'use client';

import React, { useRef, useState } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { BulletItem } from '@/types/content';
import {
  GripVertical,
  Trash2,
  Plus,
  Bold,
  Italic,
  Link as LinkIcon,
  Indent,
  Outdent,
  Sparkles,
} from 'lucide-react';
import { AiBulletModal } from '@/components/editor/ai/AiBulletModal';

interface SortableBulletProps {
  bullet: BulletItem;
  onUpdate: (patch: string | Partial<BulletItem>) => void;
  onRemove: () => void;
}

const SortableBullet: React.FC<SortableBulletProps> = ({
  bullet,
  onUpdate,
  onRemove,
}) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: bullet.id });
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [aiModalOpen, setAiModalOpen] = useState(false);

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  };

  const applyMarkup = (syntax: 'bold' | 'italic' | 'link') => {
    const el = textareaRef.current;
    if (!el) return;
    const start = el.selectionStart;
    const end = el.selectionEnd;
    const val = el.value;
    const selected = val.substring(start, end);

    let replacement = '';
    if (syntax === 'bold') {
      replacement = `**${selected || 'bold text'}**`;
    } else if (syntax === 'italic') {
      replacement = `*${selected || 'italic text'}*`;
    } else if (syntax === 'link') {
      const url = prompt('Enter URL (https://...):', 'https://');
      if (!url) return;
      replacement = `[${selected || 'link text'}](${url})`;
    }

    const nextVal = val.substring(0, start) + replacement + val.substring(end);
    onUpdate({ text: nextVal });
    setTimeout(() => {
      el.focus();
      el.setSelectionRange(start + 2, start + 2 + (selected.length || 9));
    }, 10);
  };

  const toggleIndent = (delta: number) => {
    const current = bullet.level || 0;
    const nextLevel = Math.max(0, Math.min(2, current + delta));
    onUpdate({ level: nextLevel });
  };

  const currentLevel = bullet.level || 0;

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex items-start space-x-1.5 group/bullet ${
        currentLevel === 1 ? 'ml-4' : currentLevel === 2 ? 'ml-8' : ''
      }`}
    >
      {/* Drag Handle */}
      <button
        type="button"
        {...attributes}
        {...listeners}
        className="p-1 text-slate-300 hover:text-slate-600 cursor-grab active:cursor-grabbing mt-1"
        title="Drag to reorder bullet"
      >
        <GripVertical className="w-3.5 h-3.5" />
      </button>

      {/* Bullet Input & Toolbar */}
      <div className="flex-1 flex flex-col">
        <textarea
          ref={textareaRef}
          value={bullet.text}
          rows={2}
          onChange={(e) => onUpdate({ text: e.target.value })}
          placeholder="Describe your achievement, metric, or task..."
          className="w-full text-xs px-2.5 py-1.5 border border-slate-200 rounded-t-lg focus:outline-none focus:ring-1 focus:ring-blue-500 bg-slate-50 focus:bg-white resize-y leading-relaxed"
        />

        {/* Minimal Formatting Toolbar */}
        <div className="flex items-center space-x-1 bg-slate-100 border-x border-b border-slate-200 rounded-b-lg px-2 py-0.5 text-slate-500">
          <button
            type="button"
            onClick={() => applyMarkup('bold')}
            className="p-1 hover:text-slate-900 hover:bg-slate-200 rounded text-[11px]"
            title="Bold (**text**)"
          >
            <Bold className="w-3 h-3" />
          </button>
          <button
            type="button"
            onClick={() => applyMarkup('italic')}
            className="p-1 hover:text-slate-900 hover:bg-slate-200 rounded text-[11px]"
            title="Italic (*text*)"
          >
            <Italic className="w-3 h-3" />
          </button>
          <button
            type="button"
            onClick={() => applyMarkup('link')}
            className="p-1 hover:text-slate-900 hover:bg-slate-200 rounded text-[11px]"
            title="Link [label](url)"
          >
            <LinkIcon className="w-3 h-3" />
          </button>
          <div className="h-3 w-px bg-slate-300 mx-1" />
          <button
            type="button"
            onClick={() => toggleIndent(-1)}
            disabled={currentLevel === 0}
            className="p-1 hover:text-slate-900 hover:bg-slate-200 rounded disabled:opacity-30"
            title="Outdent"
          >
            <Outdent className="w-3 h-3" />
          </button>
          <button
            type="button"
            onClick={() => toggleIndent(1)}
            disabled={currentLevel === 2}
            className="p-1 hover:text-slate-900 hover:bg-slate-200 rounded disabled:opacity-30"
            title="Indent / Sub-bullet"
          >
            <Indent className="w-3 h-3" />
          </button>
          <div className="h-3 w-px bg-slate-300 mx-1" />
          <button
            type="button"
            onClick={() => setAiModalOpen(true)}
            className="px-1.5 py-0.5 text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 rounded flex items-center gap-1 font-semibold text-[10px]"
            title="AI Bullet Assistant (Improve, Shorten, Add Impact)"
          >
            <Sparkles className="w-3 h-3" />
            <span>AI</span>
          </button>
          <div className="h-3 w-px bg-slate-300 mx-1" />
          <div className="flex items-center gap-0.5" title="Proficiency rating (1-5, user-set only)">
            {[1, 2, 3, 4, 5].map((lvl) => (
              <button
                key={lvl}
                type="button"
                onClick={() =>
                  onUpdate({
                    proficiency: bullet.proficiency === lvl ? null : lvl,
                  })
                }
                className={`w-2 h-2 rounded-full transition-transform hover:scale-125 ${
                  bullet.proficiency != null && bullet.proficiency >= lvl
                    ? 'bg-blue-600'
                    : 'bg-slate-300 hover:bg-slate-400'
                }`}
              />
            ))}
          </div>
          {currentLevel > 0 && (
            <span className="text-[9px] font-bold text-blue-600 bg-blue-100 px-1 rounded ml-auto">
              L{currentLevel}
            </span>
          )}
        </div>
      </div>

      {/* Delete Bullet */}
      <button
        type="button"
        onClick={onRemove}
        className="p-1 text-slate-300 hover:text-rose-500 transition-colors mt-1"
        title="Delete bullet"
      >
        <Trash2 className="w-3.5 h-3.5" />
      </button>

      {/* AI Bullet Modal */}
      <AiBulletModal
        initialText={bullet.text}
        isOpen={aiModalOpen}
        onClose={() => setAiModalOpen(false)}
        onAccept={(newText) => onUpdate({ text: newText })}
      />
    </div>
  );
};

interface BulletListProps {
  bullets: BulletItem[];
  onAddBullet: () => void;
  onRemoveBullet: (id: string) => void;
  onUpdateBullet: (id: string, patch: string | Partial<BulletItem>) => void;
  onReorderBullets: (oldIndex: number, newIndex: number) => void;
}

export const BulletList: React.FC<BulletListProps> = ({
  bullets,
  onAddBullet,
  onRemoveBullet,
  onUpdateBullet,
  onReorderBullets,
}) => {
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 4,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      const oldIndex = bullets.findIndex((b) => b.id === active.id);
      const newIndex = bullets.findIndex((b) => b.id === over.id);
      if (oldIndex !== -1 && newIndex !== -1) {
        onReorderBullets(oldIndex, newIndex);
      }
    }
  };

  return (
    <div className="mt-3 space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">
          Bullet Points & Accomplishments
        </label>
        <button
          type="button"
          onClick={onAddBullet}
          className="text-xs text-blue-600 hover:text-blue-700 font-semibold inline-flex items-center gap-1"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add Bullet</span>
        </button>
      </div>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={bullets.map((b) => b.id)}
          strategy={verticalListSortingStrategy}
        >
          <div className="space-y-2">
            {bullets.map((bullet) => (
              <SortableBullet
                key={bullet.id}
                bullet={bullet}
                onUpdate={(patch) => onUpdateBullet(bullet.id, patch)}
                onRemove={() => onRemoveBullet(bullet.id)}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>
    </div>
  );
};

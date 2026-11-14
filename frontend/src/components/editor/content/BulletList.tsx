'use client';

import React from 'react';
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
import { GripVertical, Trash2, Plus } from 'lucide-react';

interface SortableBulletProps {
  bullet: BulletItem;
  onUpdate: (text: string) => void;
  onRemove: () => void;
}

const SortableBullet: React.FC<SortableBulletProps> = ({
  bullet,
  onUpdate,
  onRemove,
}) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: bullet.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="flex items-start space-x-1.5 group/bullet"
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

      {/* Bullet Input */}
      <textarea
        value={bullet.text}
        rows={2}
        onChange={(e) => onUpdate(e.target.value)}
        placeholder="Describe your achievement, metric, or task..."
        className="flex-1 text-xs px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 bg-slate-50 focus:bg-white resize-y leading-relaxed"
      />

      {/* Delete Bullet */}
      <button
        type="button"
        onClick={onRemove}
        className="p-1 text-slate-300 hover:text-rose-500 transition-colors mt-1"
        title="Delete bullet"
      >
        <Trash2 className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};

interface BulletListProps {
  bullets: BulletItem[];
  onAddBullet: () => void;
  onRemoveBullet: (id: string) => void;
  onUpdateBullet: (id: string, text: string) => void;
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
    <div className="mt-2.5 pt-2 border-t border-slate-100">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
          Bullet Points
        </span>
        <button
          type="button"
          onClick={onAddBullet}
          className="text-xs text-blue-600 hover:text-blue-700 font-semibold inline-flex items-center gap-1"
        >
          <Plus className="w-3 h-3" />
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
                onUpdate={(text) => onUpdateBullet(bullet.id, text)}
                onRemove={() => onRemoveBullet(bullet.id)}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>
    </div>
  );
};

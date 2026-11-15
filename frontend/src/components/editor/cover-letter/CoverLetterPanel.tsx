'use client';

import React from 'react';
import { useResume } from '@/context/ResumeContext';
import { CoverLetterParagraph } from '@/types/content';
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
  arrayMove,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import {
  Mail,
  Building,
  User,
  MapPin,
  Calendar,
  Plus,
  Trash2,
  GripVertical,
  Send,
} from 'lucide-react';

const SortableParagraph: React.FC<{
  paragraph: CoverLetterParagraph;
  index: number;
  onUpdate: (text: string) => void;
  onRemove: () => void;
}> = ({ paragraph, index, onUpdate, onRemove }) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: paragraph.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="p-3 bg-white border border-slate-200 rounded-xl space-y-1.5 shadow-2xs group/para"
    >
      <div className="flex items-center justify-between text-slate-500">
        <div className="flex items-center space-x-1">
          <button
            type="button"
            {...attributes}
            {...listeners}
            className="p-1 text-slate-400 hover:text-slate-700 cursor-grab active:cursor-grabbing"
            title="Drag to reorder paragraph"
          >
            <GripVertical className="w-3.5 h-3.5" />
          </button>
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-600">
            Paragraph {index + 1}
          </span>
        </div>

        <button
          type="button"
          onClick={onRemove}
          className="p-1 text-slate-300 hover:text-rose-500 transition-colors"
          title="Delete paragraph"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>

      <textarea
        rows={4}
        value={paragraph.text}
        onChange={(e) => onUpdate(e.target.value)}
        placeholder="Enter paragraph text..."
        className="w-full text-xs px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 bg-slate-50 focus:bg-white resize-y leading-relaxed"
      />
    </div>
  );
};

export const CoverLetterPanel: React.FC = () => {
  const { content, updateContent } = useResume();
  const cl = content.coverLetter;

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 4 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  if (!cl) return null;

  const updateCoverLetter = (patch: Partial<typeof cl>) => {
    updateContent({
      ...content,
      coverLetter: {
        ...cl,
        ...patch,
      },
    });
  };

  const updateRecipient = (patch: Partial<typeof cl.recipient>) => {
    updateCoverLetter({
      recipient: {
        ...cl.recipient,
        ...patch,
      },
    });
  };

  const handleParagraphDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      const oldIndex = cl.paragraphs.findIndex((p) => p.id === active.id);
      const newIndex = cl.paragraphs.findIndex((p) => p.id === over.id);
      if (oldIndex !== -1 && newIndex !== -1) {
        updateCoverLetter({
          paragraphs: arrayMove(cl.paragraphs, oldIndex, newIndex),
        });
      }
    }
  };

  const addParagraph = () => {
    const newP: CoverLetterParagraph = {
      id: `p-${Date.now()}`,
      text: 'New paragraph discussing your relevant project or achievements...',
    };
    updateCoverLetter({
      paragraphs: [...cl.paragraphs, newP],
    });
  };

  const removeParagraph = (id: string) => {
    updateCoverLetter({
      paragraphs: cl.paragraphs.filter((p) => p.id !== id),
    });
  };

  const updateParagraphText = (id: string, text: string) => {
    updateCoverLetter({
      paragraphs: cl.paragraphs.map((p) => (p.id === id ? { ...p, text } : p)),
    });
  };

  return (
    <div className="p-4 pb-24 overflow-y-auto max-h-full space-y-4 text-xs text-slate-700">
      {/* 1. Recipient Information */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 space-y-3 shadow-2xs">
        <div className="flex items-center space-x-1.5 font-bold uppercase text-[11px] text-slate-500 tracking-wider">
          <Building className="w-3.5 h-3.5 text-blue-600" />
          <span>Recipient / Target Company</span>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Company Name
            </label>
            <input
              type="text"
              value={cl.recipient.company || ''}
              onChange={(e) => updateRecipient({ company: e.target.value })}
              placeholder="e.g. Stripe, Acme Corp"
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs"
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Recipient Name / Committee
            </label>
            <input
              type="text"
              value={cl.recipient.name || ''}
              onChange={(e) => updateRecipient({ name: e.target.value })}
              placeholder="e.g. Hiring Team"
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Date
            </label>
            <input
              type="text"
              value={cl.date || ''}
              onChange={(e) => updateCoverLetter({ date: e.target.value })}
              placeholder="e.g. November 14, 2026"
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs"
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Salutation
            </label>
            <input
              type="text"
              value={cl.salutation || ''}
              onChange={(e) => updateCoverLetter({ salutation: e.target.value })}
              placeholder="e.g. Dear Hiring Team,"
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs"
            />
          </div>
        </div>
      </div>

      {/* 2. Body Paragraphs with DnD Reordering */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1.5 font-bold uppercase text-[11px] text-slate-500 tracking-wider">
            <Mail className="w-3.5 h-3.5 text-blue-600" />
            <span>Letter Paragraphs</span>
          </div>
          <button
            type="button"
            onClick={addParagraph}
            className="text-xs text-blue-600 hover:text-blue-700 font-bold inline-flex items-center gap-1"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Paragraph</span>
          </button>
        </div>

        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleParagraphDragEnd}
        >
          <SortableContext
            items={cl.paragraphs.map((p) => p.id)}
            strategy={verticalListSortingStrategy}
          >
            <div className="space-y-2.5">
              {cl.paragraphs.map((para, idx) => (
                <SortableParagraph
                  key={para.id}
                  paragraph={para}
                  index={idx}
                  onUpdate={(text) => updateParagraphText(para.id, text)}
                  onRemove={() => removeParagraph(para.id)}
                />
              ))}
            </div>
          </SortableContext>
        </DndContext>
      </div>

      {/* 3. Closing & Signature */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 space-y-3 shadow-2xs">
        <div className="flex items-center space-x-1.5 font-bold uppercase text-[11px] text-slate-500 tracking-wider">
          <Send className="w-3.5 h-3.5 text-blue-600" />
          <span>Sign-off & Signature</span>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Closing Phrase
            </label>
            <input
              type="text"
              value={cl.closing || ''}
              onChange={(e) => updateCoverLetter({ closing: e.target.value })}
              placeholder="e.g. Sincerely,"
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs"
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Signature Name
            </label>
            <input
              type="text"
              value={cl.signature || ''}
              onChange={(e) => updateCoverLetter({ signature: e.target.value })}
              placeholder="e.g. Alex Mercer"
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

'use client';

import React, { useState } from 'react';
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
import { ResumeSection, SectionType } from '@/types/content';
import { useResume } from '@/context/ResumeContext';
import { HeaderForm } from './HeaderForm';
import { SectionItemCard } from './SectionItemCard';
import {
  GripVertical,
  Eye,
  EyeOff,
  Trash2,
  ChevronDown,
  ChevronRight,
  Plus,
  Briefcase,
  GraduationCap,
  Code,
  FolderGit2,
  Award,
  FileSpreadsheet,
  FileText,
} from 'lucide-react';

interface SortableSectionProps {
  section: ResumeSection;
  isExpanded: boolean;
  onToggleExpand: () => void;
}

const SortableSection: React.FC<SortableSectionProps> = ({
  section,
  isExpanded,
  onToggleExpand,
}) => {
  const {
    reorderItems,
    addItem,
    removeItem,
    updateItem,
    addBullet,
    removeBullet,
    updateBullet,
    reorderBullets,
    toggleSectionVisibility,
    removeSection,
    updateSectionTitle,
  } = useResume();

  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: section.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  };

  const itemSensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 4 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleItemDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      const oldIndex = section.items.findIndex((i) => i.id === active.id);
      const newIndex = section.items.findIndex((i) => i.id === over.id);
      if (oldIndex !== -1 && newIndex !== -1) {
        reorderItems(section.id, oldIndex, newIndex);
      }
    }
  };

  const getSectionIcon = (type: SectionType) => {
    switch (type) {
      case 'experience':
        return <Briefcase className="w-4 h-4 text-blue-600" />;
      case 'education':
        return <GraduationCap className="w-4 h-4 text-emerald-600" />;
      case 'skills':
        return <Code className="w-4 h-4 text-purple-600" />;
      case 'projects':
        return <FolderGit2 className="w-4 h-4 text-amber-600" />;
      case 'certifications':
        return <Award className="w-4 h-4 text-rose-600" />;
      case 'summary':
        return <FileSpreadsheet className="w-4 h-4 text-cyan-600" />;
      default:
        return <FileText className="w-4 h-4 text-slate-600" />;
    }
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`border rounded-xl mb-3 overflow-hidden transition-all bg-white ${
        isExpanded ? 'border-blue-400 shadow-sm ring-1 ring-blue-100' : 'border-slate-200'
      } ${!section.visible ? 'opacity-60 bg-slate-50' : ''}`}
    >
      {/* Section Header Bar */}
      <div className="flex items-center justify-between p-3 select-none">
        <div className="flex items-center space-x-2 flex-1">
          <button
            type="button"
            {...attributes}
            {...listeners}
            className="p-1 text-slate-300 hover:text-slate-600 cursor-grab active:cursor-grabbing"
            title="Drag to reorder section"
          >
            <GripVertical className="w-4 h-4" />
          </button>

          <span className="p-1 rounded bg-slate-100">{getSectionIcon(section.type)}</span>

          <input
            type="text"
            value={section.title}
            onChange={(e) => updateSectionTitle(section.id, e.target.value)}
            className="text-xs font-bold text-slate-800 bg-transparent hover:bg-slate-100 focus:bg-white focus:ring-1 focus:ring-blue-500 rounded px-1.5 py-0.5 border border-transparent hover:border-slate-300 outline-none w-48"
          />

          <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-slate-100 text-slate-500">
            {section.items?.length || 0} items
          </span>
        </div>

        {/* Section Actions: Toggle Visibility, Delete, Expand/Collapse */}
        <div className="flex items-center space-x-1">
          <button
            type="button"
            onClick={() => toggleSectionVisibility(section.id)}
            className={`p-1.5 rounded hover:bg-slate-100 transition-colors ${
              section.visible ? 'text-slate-500 hover:text-slate-800' : 'text-slate-300'
            }`}
            title={section.visible ? 'Hide section' : 'Show section'}
          >
            {section.visible ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
          </button>

          <button
            type="button"
            onClick={() => removeSection(section.id)}
            className="p-1.5 text-slate-300 hover:text-rose-500 hover:bg-slate-100 rounded transition-colors"
            title="Delete section"
          >
            <Trash2 className="w-4 h-4" />
          </button>

          <button
            type="button"
            onClick={onToggleExpand}
            className="p-1.5 text-slate-400 hover:text-slate-800 hover:bg-slate-100 rounded transition-colors"
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Expanded Items Area */}
      {isExpanded && (
        <div className="p-3 bg-slate-50 border-t border-slate-100">
          <DndContext
            sensors={itemSensors}
            collisionDetection={closestCenter}
            onDragEnd={handleItemDragEnd}
          >
            <SortableContext
              items={section.items.map((i) => i.id)}
              strategy={verticalListSortingStrategy}
            >
              {section.items.map((item) => (
                <SectionItemCard
                  key={item.id}
                  item={item}
                  sectionType={section.type}
                  onUpdate={(data) => updateItem(section.id, item.id, data)}
                  onRemove={() => removeItem(section.id, item.id)}
                  onAddBullet={() => addBullet(section.id, item.id)}
                  onRemoveBullet={(bId) => removeBullet(section.id, item.id, bId)}
                  onUpdateBullet={(bId, txt) => updateBullet(section.id, item.id, bId, txt)}
                  onReorderBullets={(oIdx, nIdx) =>
                    reorderBullets(section.id, item.id, oIdx, nIdx)
                  }
                />
              ))}
            </SortableContext>
          </DndContext>

          <button
            type="button"
            onClick={() => addItem(section.id)}
            className="w-full py-2 border-2 border-dashed border-slate-300 hover:border-blue-400 rounded-xl text-xs font-semibold text-slate-600 hover:text-blue-600 bg-white hover:bg-blue-50/50 transition-colors flex items-center justify-center space-x-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Item to {section.title}</span>
          </button>
        </div>
      )}
    </div>
  );
};

export const SectionList: React.FC = () => {
  const { content, reorderSections, addSection, activeSectionId, setActiveSectionId } =
    useResume();

  const [showAddMenu, setShowAddMenu] = useState(false);

  const sectionSensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 4 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleSectionDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      const oldIndex = content.sections.findIndex((s) => s.id === active.id);
      const newIndex = content.sections.findIndex((s) => s.id === over.id);
      if (oldIndex !== -1 && newIndex !== -1) {
        reorderSections(oldIndex, newIndex);
      }
    }
  };

  const handleAdd = (type: SectionType) => {
    addSection(type);
    setShowAddMenu(false);
  };

  return (
    <div className="p-4 pb-20 overflow-y-auto max-h-full">
      {/* 1. Header Information Form */}
      <HeaderForm />

      {/* 2. Drag-and-Drop Sections */}
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-bold text-xs uppercase tracking-wider text-slate-500">
          Sections & Items
        </h3>
        <span className="text-xs text-slate-400">Drag items or sections to reorder</span>
      </div>

      <DndContext
        sensors={sectionSensors}
        collisionDetection={closestCenter}
        onDragEnd={handleSectionDragEnd}
      >
        <SortableContext
          items={content.sections.map((s) => s.id)}
          strategy={verticalListSortingStrategy}
        >
          {content.sections.map((section) => (
            <SortableSection
              key={section.id}
              section={section}
              isExpanded={activeSectionId === section.id}
              onToggleExpand={() =>
                setActiveSectionId(activeSectionId === section.id ? null : section.id)
              }
            />
          ))}
        </SortableContext>
      </DndContext>

      {/* 3. Add Section Button & Menu */}
      <div className="relative mt-4">
        <button
          type="button"
          onClick={() => setShowAddMenu((v) => !v)}
          className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-xl shadow-sm transition-colors flex items-center justify-center space-x-1.5"
        >
          <Plus className="w-4 h-4" />
          <span>Add New Section</span>
        </button>

        {showAddMenu && (
          <div className="absolute bottom-full left-0 right-0 mb-2 bg-white border border-slate-200 rounded-xl shadow-xl p-2 z-20 grid grid-cols-2 gap-1 text-xs">
            <button
              onClick={() => handleAdd('experience')}
              className="px-3 py-2 text-left rounded-lg hover:bg-slate-100 font-medium text-slate-700 flex items-center space-x-2"
            >
              <Briefcase className="w-4 h-4 text-blue-600" />
              <span>Experience</span>
            </button>
            <button
              onClick={() => handleAdd('skills')}
              className="px-3 py-2 text-left rounded-lg hover:bg-slate-100 font-medium text-slate-700 flex items-center space-x-2"
            >
              <Code className="w-4 h-4 text-purple-600" />
              <span>Skills</span>
            </button>
            <button
              onClick={() => handleAdd('education')}
              className="px-3 py-2 text-left rounded-lg hover:bg-slate-100 font-medium text-slate-700 flex items-center space-x-2"
            >
              <GraduationCap className="w-4 h-4 text-emerald-600" />
              <span>Education</span>
            </button>
            <button
              onClick={() => handleAdd('projects')}
              className="px-3 py-2 text-left rounded-lg hover:bg-slate-100 font-medium text-slate-700 flex items-center space-x-2"
            >
              <FolderGit2 className="w-4 h-4 text-amber-600" />
              <span>Projects</span>
            </button>
            <button
              onClick={() => handleAdd('summary')}
              className="px-3 py-2 text-left rounded-lg hover:bg-slate-100 font-medium text-slate-700 flex items-center space-x-2"
            >
              <FileSpreadsheet className="w-4 h-4 text-cyan-600" />
              <span>Summary</span>
            </button>
            <button
              onClick={() => handleAdd('certifications')}
              className="px-3 py-2 text-left rounded-lg hover:bg-slate-100 font-medium text-slate-700 flex items-center space-x-2"
            >
              <Award className="w-4 h-4 text-rose-600" />
              <span>Certifications</span>
            </button>
            <button
              onClick={() => handleAdd('custom')}
              className="col-span-2 px-3 py-2 text-left rounded-lg hover:bg-slate-100 font-medium text-slate-700 flex items-center space-x-2"
            >
              <FileText className="w-4 h-4 text-slate-600" />
              <span>Custom Section</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

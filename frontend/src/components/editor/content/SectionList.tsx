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
  Copy,
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
  Scissors,
  Languages,
  BookOpen,
  HeartHandshake,
  Compass,
  Users,
  CheckSquare,
  Columns,
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
    style: resumeStyle,
    updateStyle,
    reorderItems,
    addItem,
    duplicateItem,
    removeItem,
    updateItem,
    addBullet,
    removeBullet,
    updateBullet,
    reorderBullets,
    toggleSectionVisibility,
    toggleSectionPageBreak,
    removeSection,
    duplicateSection,
    updateSectionTitle,
  } = useResume();

  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: section.id });

  const sortableStyle = {
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
      case 'awards':
        return <Award className="w-4 h-4 text-rose-600" />;
      case 'summary':
        return <FileSpreadsheet className="w-4 h-4 text-cyan-600" />;
      case 'languages':
        return <Languages className="w-4 h-4 text-indigo-600" />;
      case 'publications':
        return <BookOpen className="w-4 h-4 text-teal-600" />;
      case 'volunteering':
        return <HeartHandshake className="w-4 h-4 text-pink-600" />;
      case 'interests':
        return <Compass className="w-4 h-4 text-orange-600" />;
      case 'references':
        return <Users className="w-4 h-4 text-blue-800" />;
      default:
        return <FileText className="w-4 h-4 text-slate-600" />;
    }
  };

  const currentPlacement = resumeStyle.layout?.sectionPlacement?.[section.id] || 'main';

  const handlePlacementChange = (newPlacement: 'main' | 'sidebar' | 'full') => {
    updateStyle({
      ...resumeStyle,
      layout: {
        ...resumeStyle.layout,
        sectionPlacement: {
          ...resumeStyle.layout?.sectionPlacement,
          [section.id]: newPlacement,
        },
      },
    });
  };

  return (
    <div
      ref={setNodeRef}
      style={sortableStyle}
      className={`border rounded-2xl mb-3 overflow-hidden transition-all bg-white ${
        isExpanded ? 'border-blue-400 shadow-sm ring-1 ring-blue-100' : 'border-slate-200'
      } ${!section.visible ? 'opacity-60 bg-slate-50' : ''}`}
    >
      {/* Forced Page Break Indicator */}
      {section.pageBreakBefore && (
        <div className="bg-amber-500 text-white text-[10px] font-bold px-3 py-0.5 flex items-center justify-between">
          <span className="flex items-center gap-1">
            <Scissors className="w-3 h-3" />
            <span>Forced Page Break Before This Section</span>
          </span>
          <button
            type="button"
            onClick={() => toggleSectionPageBreak(section.id)}
            className="hover:underline opacity-80"
          >
            Remove
          </button>
        </div>
      )}

      {/* Section Header Bar */}
      <div className="flex items-center justify-between p-3 select-none">
        <div className="flex items-center space-x-2 flex-1 min-w-0">
          <button
            type="button"
            {...attributes}
            {...listeners}
            className="p-1 text-slate-300 hover:text-slate-600 cursor-grab active:cursor-grabbing shrink-0"
            title="Drag to reorder section"
          >
            <GripVertical className="w-4 h-4" />
          </button>

          <span className="p-1.5 rounded-lg bg-slate-100 shrink-0">{getSectionIcon(section.type)}</span>

          <input
            type="text"
            value={section.title}
            aria-label="Section title"
            onChange={(e) => updateSectionTitle(section.id, e.target.value)}
            className="text-xs font-bold text-slate-800 bg-transparent hover:bg-slate-100 focus:bg-white focus:ring-1 focus:ring-blue-500 rounded px-1.5 py-0.5 border border-transparent hover:border-slate-300 outline-hidden w-40 truncate"
          />

          {/* Column Target Selector */}
          <select
            value={currentPlacement}
            aria-label="Column placement on resume"
            onChange={(e) => handlePlacementChange(e.target.value as 'main' | 'sidebar' | 'full')}
            className="text-[10px] font-semibold px-2 py-0.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 border-none outline-hidden cursor-pointer shrink-0"
            title="Column placement on resume"
          >
            <option value="main">Main Col</option>
            <option value="sidebar">Sidebar</option>
            <option value="full">Full Width</option>
          </select>
        </div>

        {/* Section Actions: Toggle Page Break, Visibility, Duplicate, Delete, Expand/Collapse */}
        <div className="flex items-center space-x-1 shrink-0">
          {/* Page break before section */}
          <button
            type="button"
            onClick={() => toggleSectionPageBreak(section.id)}
            aria-label={section.pageBreakBefore ? "Remove page break before section" : "Force page break before this section"}
            className={`p-1.5 rounded transition-colors ${
              section.pageBreakBefore
                ? 'text-amber-600 bg-amber-50 hover:bg-amber-100'
                : 'text-slate-300 hover:text-slate-600 hover:bg-slate-100'
            }`}
            title={
              section.pageBreakBefore
                ? 'Remove page break before section'
                : 'Force page break before this section'
            }
          >
            <Scissors className="w-3.5 h-3.5" />
          </button>

          {/* Visibility Toggle */}
          <button
            type="button"
            onClick={() => toggleSectionVisibility(section.id)}
            aria-label={section.visible ? "Hide section on resume" : "Show section on resume"}
            className={`p-1.5 rounded hover:bg-slate-100 transition-colors ${
              section.visible ? 'text-slate-500 hover:text-slate-800' : 'text-slate-300'
            }`}
            title={section.visible ? 'Hide section' : 'Show section'}
          >
            {section.visible ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
          </button>

          {/* Duplicate Section */}
          <button
            type="button"
            onClick={() => duplicateSection(section.id)}
            aria-label="Duplicate section"
            className="p-1.5 text-slate-300 hover:text-blue-600 hover:bg-slate-100 rounded transition-colors"
            title="Duplicate section"
          >
            <Copy className="w-3.5 h-3.5" />
          </button>

          {/* Delete section */}
          <button
            type="button"
            onClick={() => removeSection(section.id)}
            aria-label="Delete section"
            className="p-1.5 text-slate-300 hover:text-rose-500 hover:bg-slate-100 rounded transition-colors"
            title="Delete section"
          >
            <Trash2 className="w-4 h-4" />
          </button>

          {/* Expand / Collapse */}
          <button
            type="button"
            onClick={onToggleExpand}
            aria-label={isExpanded ? "Collapse section" : "Expand section"}
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
                  onDuplicate={() => duplicateItem(section.id, item.id)}
                  onRemove={() => removeItem(section.id, item.id)}
                  onAddBullet={() => addBullet(section.id, item.id)}
                  onRemoveBullet={(bId) => removeBullet(section.id, item.id, bId)}
                  onUpdateBullet={(bId, patch) => updateBullet(section.id, item.id, bId, patch)}
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
            className="w-full py-2.5 border-2 border-dashed border-slate-300 hover:border-blue-400 rounded-xl text-xs font-semibold text-slate-600 hover:text-blue-600 bg-white hover:bg-blue-50/50 transition-colors flex items-center justify-center space-x-1.5 shadow-2xs"
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

  const handleAdd = (type: SectionType, customTitle?: string) => {
    if (type === 'custom' && !customTitle) {
      const name = prompt('Enter name for custom section:', 'Additional Information');
      if (!name) return;
      addSection('custom', name);
    } else {
      addSection(type, customTitle);
    }
    setShowAddMenu(false);
  };

  return (
    <div className="p-4 pb-24 overflow-y-auto max-h-full">
      {/* 1. Header Information Form */}
      <HeaderForm />

      {/* 2. Drag-and-Drop Sections */}
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-bold text-xs uppercase tracking-wider text-slate-500">
          Sections & Items
        </h3>
        <span className="text-xs text-slate-400">Drag handle to reorder</span>
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

      {/* 3. Add Section Button & Expanded Menu */}
      <div className="relative mt-4">
        <button
          type="button"
          onClick={() => setShowAddMenu((v) => !v)}
          className="w-full py-3 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-2xl shadow-xs transition-colors flex items-center justify-center space-x-1.5"
        >
          <Plus className="w-4 h-4" />
          <span>Add Section</span>
        </button>

        {showAddMenu && (
          <div className="absolute bottom-full left-0 right-0 mb-2 bg-white border border-slate-200 rounded-2xl shadow-2xl p-3 z-30 grid grid-cols-2 gap-2 text-xs max-h-96 overflow-y-auto animate-in fade-in zoom-in-95">
            <button
              onClick={() => handleAdd('experience')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-700 flex items-center space-x-2 transition-colors"
            >
              <Briefcase className="w-4 h-4 text-blue-600" />
              <span>Experience</span>
            </button>
            <button
              onClick={() => handleAdd('skills')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-700 flex items-center space-x-2 transition-colors"
            >
              <Code className="w-4 h-4 text-purple-600" />
              <span>Skills (Grouped)</span>
            </button>
            <button
              onClick={() => handleAdd('education')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-700 flex items-center space-x-2 transition-colors"
            >
              <GraduationCap className="w-4 h-4 text-emerald-600" />
              <span>Education</span>
            </button>
            <button
              onClick={() => handleAdd('projects')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-700 flex items-center space-x-2 transition-colors"
            >
              <FolderGit2 className="w-4 h-4 text-amber-600" />
              <span>Projects</span>
            </button>
            <button
              onClick={() => handleAdd('summary')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-700 flex items-center space-x-2 transition-colors"
            >
              <FileSpreadsheet className="w-4 h-4 text-cyan-600" />
              <span>Summary</span>
            </button>
            <button
              onClick={() => handleAdd('certifications')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-700 flex items-center space-x-2 transition-colors"
            >
              <Award className="w-4 h-4 text-rose-600" />
              <span>Certifications</span>
            </button>
            <button
              onClick={() => handleAdd('languages')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-700 flex items-center space-x-2 transition-colors"
            >
              <Languages className="w-4 h-4 text-indigo-600" />
              <span>Languages</span>
            </button>
            <button
              onClick={() => handleAdd('awards')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-700 flex items-center space-x-2 transition-colors"
            >
              <Award className="w-4 h-4 text-amber-500" />
              <span>Honors & Awards</span>
            </button>
            <button
              onClick={() => handleAdd('publications')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-700 flex items-center space-x-2 transition-colors"
            >
              <BookOpen className="w-4 h-4 text-teal-600" />
              <span>Publications</span>
            </button>
            <button
              onClick={() => handleAdd('volunteering')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-700 flex items-center space-x-2 transition-colors"
            >
              <HeartHandshake className="w-4 h-4 text-pink-600" />
              <span>Volunteering</span>
            </button>
            <button
              onClick={() => handleAdd('interests')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-700 flex items-center space-x-2 transition-colors"
            >
              <Compass className="w-4 h-4 text-orange-600" />
              <span>Interests</span>
            </button>
            <button
              onClick={() => handleAdd('references')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-700 flex items-center space-x-2 transition-colors"
            >
              <Users className="w-4 h-4 text-blue-800" />
              <span>References</span>
            </button>
            <button
              onClick={() => handleAdd('custom', 'Declaration')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-700 flex items-center space-x-2 transition-colors"
            >
              <CheckSquare className="w-4 h-4 text-emerald-600" />
              <span>Declaration</span>
            </button>
            <button
              onClick={() => handleAdd('custom')}
              className="px-3 py-2 text-left rounded-xl bg-blue-50 hover:bg-blue-100 font-semibold text-blue-700 flex items-center space-x-2 transition-colors"
            >
              <FileText className="w-4 h-4 text-blue-600" />
              <span>+ Custom Section</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

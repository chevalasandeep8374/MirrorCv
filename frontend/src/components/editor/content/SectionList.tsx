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
  Folder,
  FolderGit2,
  Award,
  FileSpreadsheet,
  FileText,
  Lightbulb,
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
        return <Briefcase className="w-5 h-5 text-slate-800" />;
      case 'education':
        return <GraduationCap className="w-5 h-5 text-slate-800" />;
      case 'skills':
        return <Lightbulb className="w-5 h-5 text-slate-800" />;
      case 'projects':
        return <Folder className="w-5 h-5 text-slate-800" />;
      case 'certifications':
      case 'awards':
        return <Award className="w-5 h-5 text-slate-800" />;
      case 'summary':
        return <FileText className="w-5 h-5 text-slate-800" />;
      case 'languages':
        return <Languages className="w-5 h-5 text-slate-800" />;
      case 'publications':
        return <BookOpen className="w-5 h-5 text-slate-800" />;
      case 'volunteering':
        return <HeartHandshake className="w-5 h-5 text-slate-800" />;
      case 'interests':
        return <Compass className="w-5 h-5 text-slate-800" />;
      case 'references':
        return <Users className="w-5 h-5 text-slate-800" />;
      default:
        return <FileText className="w-5 h-5 text-slate-800" />;
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
      className={`border rounded-2xl mb-3.5 overflow-hidden transition-all bg-white group ${
        isExpanded
          ? 'border-slate-300 shadow-sm ring-1 ring-slate-100'
          : 'border-slate-200/90 shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:border-slate-300'
      } ${!section.visible ? 'opacity-65 bg-slate-50/70' : ''}`}
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

      {/* Dropdown Stage Trigger Bar */}
      <div
        onClick={onToggleExpand}
        className="p-4 sm:p-4.5 flex items-center justify-between cursor-pointer select-none bg-white hover:bg-slate-50/50 transition-colors"
      >
        <div className="flex items-center space-x-2.5 min-w-0">
          <button
            type="button"
            {...attributes}
            {...listeners}
            onClick={(e) => e.stopPropagation()}
            className="p-1 -ml-1 text-slate-300 hover:text-slate-600 opacity-0 group-hover:opacity-100 cursor-grab active:cursor-grabbing shrink-0 transition-opacity"
            title="Drag to reorder section"
          >
            <GripVertical className="w-4 h-4" />
          </button>

          <span className="shrink-0">{getSectionIcon(section.type)}</span>

          <div className="min-w-0">
            <h3 className="font-bold text-slate-900 text-[15px] sm:text-[16px] tracking-tight truncate">
              {section.title}
            </h3>
          </div>
        </div>

        {/* Right Actions & Chevron */}
        <div className="flex items-center space-x-2 shrink-0" onClick={(e) => e.stopPropagation()}>
          {/* Quick Visibility Eye Toggle */}
          <button
            type="button"
            onClick={() => toggleSectionVisibility(section.id)}
            aria-label={section.visible ? "Hide section on resume" : "Show section on resume"}
            className={`p-1.5 rounded-lg transition-colors ${
              section.visible
                ? 'text-slate-400 hover:text-slate-700 opacity-0 group-hover:opacity-100 hover:bg-slate-100'
                : 'text-amber-500 bg-amber-50 hover:bg-amber-100'
            }`}
            title={section.visible ? 'Hide section' : 'Show section'}
          >
            {section.visible ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
          </button>

          {/* Chevron */}
          <button
            type="button"
            onClick={onToggleExpand}
            aria-label={isExpanded ? "Collapse section" : "Expand section"}
            className="p-1 text-slate-400 group-hover:text-slate-700 transition-colors"
          >
            <ChevronDown
              className={`w-5 h-5 transition-transform duration-200 ${
                isExpanded ? 'rotate-180' : ''
              }`}
            />
          </button>
        </div>
      </div>

      {/* Expanded Stage Body */}
      {isExpanded && (
        <div className="p-3 sm:p-4 bg-[#FAFBFD] border-t border-slate-100 space-y-3">
          {/* Internal Section Toolbar */}
          <div className="flex flex-wrap items-center justify-between gap-2 p-2 bg-white border border-slate-200/80 rounded-xl">
            <div className="flex items-center space-x-2 flex-1 min-w-[180px]">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wide">Title:</span>
              <input
                type="text"
                value={section.title}
                aria-label="Section title"
                onChange={(e) => updateSectionTitle(section.id, e.target.value)}
                className="text-xs font-bold text-slate-800 bg-slate-50 focus:bg-white focus:ring-1 focus:ring-blue-500 rounded px-2 py-1 border border-slate-200 outline-hidden flex-1"
              />
            </div>

            <div className="flex items-center space-x-1.5 shrink-0">
              {/* Column Target Selector */}
              <select
                value={currentPlacement}
                aria-label="Column placement on resume"
                onChange={(e) => handlePlacementChange(e.target.value as 'main' | 'sidebar' | 'full')}
                className="text-[11px] font-semibold px-2 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 border-none outline-hidden cursor-pointer"
                title="Column placement on resume"
              >
                <option value="main">Main Column</option>
                <option value="sidebar">Sidebar</option>
                <option value="full">Full Width</option>
              </select>

              {/* Page break toggle */}
              <button
                type="button"
                onClick={() => toggleSectionPageBreak(section.id)}
                className={`p-1.5 rounded-lg transition-colors ${
                  section.pageBreakBefore
                    ? 'text-amber-600 bg-amber-50 hover:bg-amber-100'
                    : 'text-slate-400 hover:text-slate-700 hover:bg-slate-100'
                }`}
                title={section.pageBreakBefore ? 'Remove page break before section' : 'Force page break before this section'}
              >
                <Scissors className="w-3.5 h-3.5" />
              </button>

              {/* Duplicate Section */}
              <button
                type="button"
                onClick={() => duplicateSection(section.id)}
                className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-slate-100 rounded-lg transition-colors"
                title="Duplicate section"
              >
                <Copy className="w-3.5 h-3.5" />
              </button>

              {/* Delete section */}
              <button
                type="button"
                onClick={() => removeSection(section.id)}
                className="p-1.5 text-slate-400 hover:text-rose-500 hover:bg-slate-100 rounded-lg transition-colors"
                title="Delete section"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Section Items Dnd List */}
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
            className="w-full py-2.5 border-2 border-dashed border-slate-300 hover:border-slate-400 rounded-xl text-xs font-semibold text-slate-600 hover:text-slate-900 bg-white hover:bg-slate-50 transition-colors flex items-center justify-center space-x-1.5 shadow-2xs cursor-pointer"
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
    <div className="relative flex flex-col h-full">
      {/* Scrollable Stage Cards Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-5 pb-28">
        {/* 1. Personal Details Stage Card */}
        <HeaderForm />

        {/* 2. Drag-and-Drop Dropdown Stage Cards */}
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
      </div>

      {/* 3. Floating Bottom "+ Add Content" Button & Menu */}
      <div className="sticky bottom-0 left-0 right-0 py-4 bg-gradient-to-t from-[#F8F9FA] via-[#F8F9FA]/90 to-transparent flex flex-col items-center justify-center z-20 px-4">
        {showAddMenu && (
          <div className="w-full max-w-md mb-3 bg-white border border-slate-200/90 rounded-2xl shadow-2xl p-3 z-30 grid grid-cols-2 gap-2 text-xs max-h-80 overflow-y-auto animate-in fade-in zoom-in-95">
            <button
              onClick={() => handleAdd('summary')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-800 flex items-center space-x-2.5 transition-colors"
            >
              <FileText className="w-4 h-4 text-slate-800" />
              <span>Summary</span>
            </button>
            <button
              onClick={() => handleAdd('skills')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-800 flex items-center space-x-2.5 transition-colors"
            >
              <Lightbulb className="w-4 h-4 text-slate-800" />
              <span>Technical Skills</span>
            </button>
            <button
              onClick={() => handleAdd('experience')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-800 flex items-center space-x-2.5 transition-colors"
            >
              <Briefcase className="w-4 h-4 text-slate-800" />
              <span>Experience</span>
            </button>
            <button
              onClick={() => handleAdd('projects')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-800 flex items-center space-x-2.5 transition-colors"
            >
              <Folder className="w-4 h-4 text-slate-800" />
              <span>Projects</span>
            </button>
            <button
              onClick={() => handleAdd('education')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-800 flex items-center space-x-2.5 transition-colors"
            >
              <GraduationCap className="w-4 h-4 text-slate-800" />
              <span>Education</span>
            </button>
            <button
              onClick={() => handleAdd('certifications')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-800 flex items-center space-x-2.5 transition-colors"
            >
              <Award className="w-4 h-4 text-slate-800" />
              <span>Certifications</span>
            </button>
            <button
              onClick={() => handleAdd('languages')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-800 flex items-center space-x-2.5 transition-colors"
            >
              <Languages className="w-4 h-4 text-slate-800" />
              <span>Languages</span>
            </button>
            <button
              onClick={() => handleAdd('awards')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-800 flex items-center space-x-2.5 transition-colors"
            >
              <Award className="w-4 h-4 text-slate-800" />
              <span>Honors & Awards</span>
            </button>
            <button
              onClick={() => handleAdd('publications')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-800 flex items-center space-x-2.5 transition-colors"
            >
              <BookOpen className="w-4 h-4 text-slate-800" />
              <span>Publications</span>
            </button>
            <button
              onClick={() => handleAdd('volunteering')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-800 flex items-center space-x-2.5 transition-colors"
            >
              <HeartHandshake className="w-4 h-4 text-slate-800" />
              <span>Volunteering</span>
            </button>
            <button
              onClick={() => handleAdd('interests')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-800 flex items-center space-x-2.5 transition-colors"
            >
              <Compass className="w-4 h-4 text-slate-800" />
              <span>Interests</span>
            </button>
            <button
              onClick={() => handleAdd('references')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-800 flex items-center space-x-2.5 transition-colors"
            >
              <Users className="w-4 h-4 text-slate-800" />
              <span>References</span>
            </button>
            <button
              onClick={() => handleAdd('custom', 'Declaration')}
              className="px-3 py-2 text-left rounded-xl hover:bg-slate-100 font-semibold text-slate-800 flex items-center space-x-2.5 transition-colors"
            >
              <CheckSquare className="w-4 h-4 text-slate-800" />
              <span>Declaration</span>
            </button>
            <button
              onClick={() => handleAdd('custom')}
              className="px-3 py-2 text-left rounded-xl bg-pink-50 hover:bg-pink-100 font-semibold text-[#FF2D6C] flex items-center space-x-2.5 transition-colors"
            >
              <Plus className="w-4 h-4 text-[#FF2D6C]" />
              <span>+ Custom Section</span>
            </button>
          </div>
        )}

        <button
          type="button"
          onClick={() => setShowAddMenu((v) => !v)}
          className="bg-gradient-to-r from-[#FF2D6C] to-[#FF5E62] hover:opacity-95 text-white font-bold text-sm px-8 py-3 rounded-full shadow-lg shadow-pink-500/25 hover:shadow-pink-500/35 active:scale-[0.98] transition-all flex items-center justify-center gap-2 cursor-pointer select-none"
        >
          <Plus className="w-4 h-4 stroke-[2.5]" />
          <span>Add Content</span>
        </button>
      </div>
    </div>
  );
};

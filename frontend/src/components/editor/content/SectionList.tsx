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
  Plus,
  Briefcase,
  GraduationCap,
  Award,
  FileText,
  Lightbulb,
  Scissors,
  Languages,
  BookOpen,
  HeartHandshake,
  Compass,
  Users,
  CheckSquare,
  Sparkles,
  Edit2,
  Check,
  ArrowUpDown,
  Folder,
  SlidersHorizontal,
  Bot,
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
    updateSectionTitle,
  } = useResume();

  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editedTitle, setEditedTitle] = useState(section.title);

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
      case 'summary':
        return (
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center shrink-0">
            <FileText className="w-4 h-4" />
          </div>
        );
      case 'experience':
        return (
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center shrink-0">
            <Briefcase className="w-4 h-4" />
          </div>
        );
      case 'skills':
        return (
          <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-700 flex items-center justify-center shrink-0">
            <Lightbulb className="w-4 h-4" />
          </div>
        );
      case 'education':
        return (
          <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center shrink-0">
            <GraduationCap className="w-4 h-4" />
          </div>
        );
      case 'projects':
        return (
          <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center shrink-0">
            <Folder className="w-4 h-4" />
          </div>
        );
      case 'certifications':
        return (
          <div className="w-8 h-8 rounded-lg bg-rose-50 text-rose-700 flex items-center justify-center shrink-0">
            <Award className="w-4 h-4" />
          </div>
        );
      case 'languages':
        return (
          <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-700 flex items-center justify-center shrink-0">
            <Languages className="w-4 h-4" />
          </div>
        );
      default:
        return (
          <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center shrink-0">
            <FileText className="w-4 h-4" />
          </div>
        );
    }
  };

  const getAddButtonLabel = (type: SectionType) => {
    switch (type) {
      case 'experience':
        return 'Add Role';
      case 'skills':
        return 'Add Entry';
      case 'education':
        return 'Add Education';
      case 'projects':
        return 'Add Project';
      case 'certifications':
        return 'Add Certification';
      default:
        return 'Add Entry';
    }
  };

  const getAiButtonLabel = (type: SectionType) => {
    switch (type) {
      case 'summary':
        return 'AI Polish';
      case 'skills':
        return 'AI Skill Suggestions';
      case 'experience':
        return 'AI Suggestions';
      default:
        return 'AI Suggestions';
    }
  };

  const handleSaveTitle = () => {
    if (editedTitle.trim()) {
      updateSectionTitle(section.id, editedTitle.trim());
    }
    setIsEditingTitle(false);
  };

  // Special handling for summary section
  const isSummarySection = section.type === 'summary';
  const summaryItem = section.items?.[0];
  const summaryText = summaryItem?.bullets?.[0]?.text || '';
  const wordCount = summaryText ? summaryText.trim().split(/\s+/).length : 0;
  const charCount = summaryText.length;

  return (
    <div
      ref={setNodeRef}
      style={sortableStyle}
      className={`border rounded-xl mb-3.5 overflow-hidden transition-all bg-white group shadow-sm ${
        isExpanded
          ? 'border-slate-300 ring-1 ring-slate-100'
          : 'border-slate-200/90 hover:border-slate-300'
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
            className="hover:underline opacity-80 cursor-pointer"
          >
            Remove
          </button>
        </div>
      )}

      {/* Stage Summary Trigger Header */}
      <div
        onClick={onToggleExpand}
        className="p-3.5 sm:p-4 flex items-center justify-between cursor-pointer select-none bg-white hover:bg-slate-50/60 transition-colors"
      >
        <div className="flex items-center gap-2.5 min-w-0">
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

          {getSectionIcon(section.type)}

          <div className="flex items-center gap-2 min-w-0">
            {isEditingTitle ? (
              <div className="flex items-center gap-1.5" onClick={(e) => e.stopPropagation()}>
                <input
                  type="text"
                  value={editedTitle}
                  onChange={(e) => setEditedTitle(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSaveTitle();
                    if (e.key === 'Escape') setIsEditingTitle(false);
                  }}
                  autoFocus
                  className="font-bold text-[16px] text-slate-900 border border-blue-400 rounded px-2 py-0.5 focus:outline-none"
                />
                <button
                  type="button"
                  onClick={handleSaveTitle}
                  className="p-1 text-emerald-600 hover:bg-emerald-50 rounded"
                >
                  <Check className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <>
                <h3 className="font-bold text-[16px] text-slate-900 tracking-tight truncate">
                  {section.title}
                </h3>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditedTitle(section.title);
                    setIsEditingTitle(true);
                  }}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 hover:text-slate-900 text-xs font-medium transition-colors shadow-2xs ml-1 cursor-pointer"
                  title="Edit Heading Name"
                >
                  <Edit2 className="w-3 h-3 text-slate-400" />
                  <span>Edit Heading</span>
                </button>
              </>
            )}
          </div>
        </div>

        {/* Right Actions & Chevron */}
        <div className="flex items-center gap-2 shrink-0" onClick={(e) => e.stopPropagation()}>
          <button
            type="button"
            onClick={() => toggleSectionVisibility(section.id)}
            aria-label={section.visible ? 'Hide section on resume' : 'Show section on resume'}
            className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
              section.visible
                ? 'text-slate-400 hover:text-slate-800 hover:bg-slate-100'
                : 'text-amber-500 bg-amber-50 hover:bg-amber-100'
            }`}
            title={section.visible ? 'Toggle visibility in resume' : 'Show section'}
          >
            {section.visible ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
          </button>

          <button
            type="button"
            onClick={onToggleExpand}
            aria-label={isExpanded ? 'Collapse section' : 'Expand section'}
            className="p-1 text-slate-400 hover:text-slate-800 transition-colors cursor-pointer"
          >
            <ChevronDown
              className={`w-4 h-4 transition-transform duration-200 ${
                isExpanded ? 'rotate-180' : ''
              }`}
            />
          </button>
        </div>
      </div>

      {/* Expanded Stage Body */}
      {isExpanded && (
        <div className="border-t border-slate-100">
          {/* Summary Section Special View */}
          {isSummarySection ? (
            <div className="px-4 pb-4 pt-3 space-y-3">
              <div className="flex items-center justify-between pb-1">
                <span className="text-xs font-medium text-slate-400">Editorial Rich Text</span>
                <div className="flex items-center gap-1.5">
                  <button
                    type="button"
                    onClick={() => {
                      if (!summaryItem) {
                        addItem(section.id);
                      }
                    }}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-[#FFF0F5] border border-[#FFD5DF] text-[#FF2D6C] text-xs font-semibold hover:bg-pink-100 transition-colors cursor-pointer"
                    title="Improve phrasing and impact with AI"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>AI Polish</span>
                  </button>
                  <button
                    type="button"
                    className="inline-flex items-center gap-1 px-2 py-1 rounded-md border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-medium transition-colors cursor-pointer"
                    title="Highlight tailored job keywords"
                  >
                    <SlidersHorizontal className="w-3 h-3 text-slate-400" />
                    <span>Match JD</span>
                  </button>
                </div>
              </div>

              <textarea
                rows={4}
                value={summaryText}
                onChange={(e) => {
                  const newText = e.target.value;
                  if (summaryItem) {
                    if (summaryItem.bullets && summaryItem.bullets.length > 0) {
                      updateBullet(section.id, summaryItem.id, summaryItem.bullets[0].id, {
                        text: newText,
                      });
                    } else {
                      addBullet(section.id, summaryItem.id);
                    }
                  } else {
                    addItem(section.id);
                  }
                }}
                placeholder="Write a concise professional summary highlighting your key achievements and core competencies..."
                className="w-full p-3 bg-slate-50/70 rounded-md border border-slate-200 text-slate-900 text-xs focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#181824] transition-all leading-relaxed resize-none"
              />

              <div className="flex items-center justify-between text-[11px] text-slate-400 pt-0.5">
                <span>
                  Word count: {wordCount} words · {charCount} characters
                </span>
                <span className="text-emerald-700 font-medium flex items-center gap-1">
                  <Check className="w-3 h-3 text-emerald-600" />
                  <span>Strong executive tone</span>
                </span>
              </div>
            </div>
          ) : (
            /* Standard Section Items Dnd List */
            <div className="p-3 sm:p-4 space-y-3">
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
            </div>
          )}

          {/* Bottom Action Toolbar matching FlowCV & Stitch pattern */}
          <div className="p-3.5 bg-slate-50/60 border-t border-slate-100 flex items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              {/* Primary Add Button */}
              <button
                type="button"
                onClick={() => addItem(section.id)}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-800 text-xs font-semibold transition-colors cursor-pointer shadow-2xs"
              >
                <Plus className="w-4 h-4" />
                <span>{getAddButtonLabel(section.type)}</span>
              </button>

              {/* AI Suggestions Button (Vibrant Purple FlowCV styling #5A32EA) */}
              <button
                type="button"
                onClick={() => {
                  // Trigger smart assistance or open AI tools
                  alert(`AI assistant generating tailored suggestions for ${section.title}...`);
                }}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#5A32EA] hover:bg-[#4C28CF] text-white text-xs font-semibold transition-colors cursor-pointer shadow-xs"
              >
                <Bot className="w-4 h-4" />
                <span>{getAiButtonLabel(section.type)}</span>
              </button>
            </div>

            {/* Delete Section Button */}
            <button
              type="button"
              onClick={() => {
                if (confirm(`Are you sure you want to delete the "${section.title}" section?`)) {
                  removeSection(section.id);
                }
              }}
              className="w-9 h-9 rounded-lg border border-slate-200 bg-white hover:bg-rose-50 hover:text-rose-600 hover:border-rose-200 text-slate-500 flex items-center justify-center transition-colors cursor-pointer"
              title="Delete Section"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export const SectionList: React.FC = () => {
  const { content, reorderSections, addSection, activeSectionId, setActiveSectionId } =
    useResume();

  const [showAddMenu, setShowAddMenu] = useState(false);
  const [allCollapsed, setAllCollapsed] = useState(false);
  const [personalExpanded, setPersonalExpanded] = useState(true);

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

  const handleToggleCollapseAll = () => {
    if (allCollapsed) {
      // Expand
      setPersonalExpanded(true);
      if (content.sections.length > 0) {
        setActiveSectionId(content.sections[0].id);
      }
      setAllCollapsed(false);
    } else {
      // Collapse all
      setPersonalExpanded(false);
      setActiveSectionId(null);
      setAllCollapsed(true);
    }
  };

  // Count active/visible sections including personal details
  const activeSectionsCount =
    content.sections.filter((s) => s.visible !== false).length + (content.header ? 1 : 0);

  return (
    <div className="relative flex flex-col h-full bg-[#F8F9FA]">
      {/* Top Sub-bar / Stage Controls Filter Header */}
      <div className="px-5 py-3 border-b border-slate-200/90 flex items-center justify-between bg-[#F8F9FA]/90 backdrop-blur-xs sticky top-0 z-20">
        <div className="flex items-center gap-2">
          <span className="font-bold text-sm text-slate-900">Resume Sections</span>
          <span className="px-2 py-0.5 rounded-full bg-white border border-slate-200 font-mono text-[11px] text-slate-600 font-medium">
            {activeSectionsCount} Active
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={handleToggleCollapseAll}
            className="text-xs font-medium text-slate-500 hover:text-slate-900 transition-colors cursor-pointer px-2 py-1 rounded hover:bg-white"
            title={allCollapsed ? 'Expand all sections' : 'Collapse all sections'}
          >
            {allCollapsed ? 'Expand All' : 'Collapse All'}
          </button>
          <button
            type="button"
            className="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-white transition-colors cursor-pointer"
            title="Reorder sections"
          >
            <ArrowUpDown className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Scrollable Stage Cards Container */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-5 pb-28">
        {/* STAGE 1: Personal Details */}
        <HeaderForm
          isExpanded={personalExpanded}
          onToggleExpand={() => setPersonalExpanded((prev) => !prev)}
        />

        {/* STAGES 2+: Sortable Section Cards */}
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
                onToggleExpand={() => {
                  setActiveSectionId(activeSectionId === section.id ? null : section.id);
                  if (allCollapsed) setAllCollapsed(false);
                }}
              />
            ))}
          </SortableContext>
        </DndContext>
      </div>

      {/* Floating Bottom Sticky CTA: "+ Add Content" Capsule Button */}
      <div className="absolute bottom-5 left-0 right-0 flex justify-center px-5 pointer-events-none z-30">
        <button
          type="button"
          onClick={() => setShowAddMenu((v) => !v)}
          className="pointer-events-auto inline-flex items-center gap-2 px-6 py-3 rounded-full bg-gradient-to-r from-[#FF2D6C] to-[#FF5E62] text-white font-bold text-sm shadow-lg shadow-pink-500/25 hover:brightness-105 active:scale-95 transition-all cursor-pointer select-none"
        >
          <Plus className="w-4 h-4 stroke-[2.5]" />
          <span>Add Content</span>
        </button>
      </div>

      {/* Popup 2-Column Menu for Adding Sections */}
      {showAddMenu && (
        <div className="absolute bottom-20 left-6 right-6 bg-white rounded-xl border border-slate-200 shadow-2xl p-4 z-40 animate-in fade-in zoom-in-95">
          <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-200">
            <div>
              <span className="font-bold text-sm text-slate-900 block">Add Resume Section</span>
              <span className="text-xs text-slate-500">
                Choose a module to append to your resume
              </span>
            </div>
            <button
              type="button"
              onClick={() => setShowAddMenu(false)}
              className="w-6 h-6 rounded-full hover:bg-slate-100 flex items-center justify-center text-slate-400 hover:text-slate-800 cursor-pointer"
            >
              ×
            </button>
          </div>
          <div className="grid grid-cols-2 gap-2 text-left">
            <button
              type="button"
              onClick={() => handleAdd('summary')}
              className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-slate-100 text-slate-800 text-xs font-medium border border-transparent hover:border-slate-200 transition-all cursor-pointer"
            >
              <FileText className="w-4 h-4 text-slate-800" />
              <span>Summary</span>
            </button>
            <button
              type="button"
              onClick={() => handleAdd('experience')}
              className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-slate-100 text-slate-800 text-xs font-medium border border-transparent hover:border-slate-200 transition-all cursor-pointer"
            >
              <Briefcase className="w-4 h-4 text-slate-800" />
              <span>Work Experience</span>
            </button>
            <button
              type="button"
              onClick={() => handleAdd('skills')}
              className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-slate-100 text-slate-800 text-xs font-medium border border-transparent hover:border-slate-200 transition-all cursor-pointer"
            >
              <Lightbulb className="w-4 h-4 text-slate-800" />
              <span>Skills</span>
            </button>
            <button
              type="button"
              onClick={() => handleAdd('education')}
              className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-slate-100 text-slate-800 text-xs font-medium border border-transparent hover:border-slate-200 transition-all cursor-pointer"
            >
              <GraduationCap className="w-4 h-4 text-slate-800" />
              <span>Education</span>
            </button>
            <button
              type="button"
              onClick={() => handleAdd('projects')}
              className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-slate-100 text-slate-800 text-xs font-medium border border-transparent hover:border-slate-200 transition-all cursor-pointer"
            >
              <Folder className="w-4 h-4 text-slate-800" />
              <span>Projects</span>
            </button>
            <button
              type="button"
              onClick={() => handleAdd('certifications')}
              className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-slate-100 text-slate-800 text-xs font-medium border border-transparent hover:border-slate-200 transition-all cursor-pointer"
            >
              <Award className="w-4 h-4 text-slate-800" />
              <span>Certifications</span>
            </button>
            <button
              type="button"
              onClick={() => handleAdd('languages')}
              className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-slate-100 text-slate-800 text-xs font-medium border border-transparent hover:border-slate-200 transition-all cursor-pointer"
            >
              <Languages className="w-4 h-4 text-slate-800" />
              <span>Languages</span>
            </button>
            <button
              type="button"
              onClick={() => handleAdd('awards')}
              className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-slate-100 text-slate-800 text-xs font-medium border border-transparent hover:border-slate-200 transition-all cursor-pointer"
            >
              <Award className="w-4 h-4 text-slate-800" />
              <span>Awards &amp; Honors</span>
            </button>
            <button
              type="button"
              onClick={() => handleAdd('custom')}
              className="col-span-2 flex items-center justify-center gap-2 p-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold border border-slate-200 transition-all cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>+ Custom Section</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

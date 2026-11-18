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
          <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-800 flex items-center justify-center shrink-0 group-hover:bg-slate-200/80 transition-colors">
            <FileText className="w-4 h-4" />
          </div>
        );
      case 'experience':
        return (
          <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-800 flex items-center justify-center shrink-0 group-hover:bg-slate-200/80 transition-colors">
            <Briefcase className="w-4 h-4" />
          </div>
        );
      case 'skills':
        return (
          <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-800 flex items-center justify-center shrink-0 group-hover:bg-slate-200/80 transition-colors">
            <Lightbulb className="w-4 h-4" />
          </div>
        );
      case 'education':
        return (
          <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-800 flex items-center justify-center shrink-0 group-hover:bg-slate-200/80 transition-colors">
            <GraduationCap className="w-4 h-4" />
          </div>
        );
      case 'projects':
        return (
          <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-800 flex items-center justify-center shrink-0 group-hover:bg-slate-200/80 transition-colors">
            <Folder className="w-4 h-4" />
          </div>
        );
      case 'certifications':
        return (
          <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-800 flex items-center justify-center shrink-0 group-hover:bg-slate-200/80 transition-colors">
            <Award className="w-4 h-4" />
          </div>
        );
      case 'languages':
        return (
          <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-800 flex items-center justify-center shrink-0 group-hover:bg-slate-200/80 transition-colors">
            <Languages className="w-4 h-4" />
          </div>
        );
      default:
        return (
          <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-800 flex items-center justify-center shrink-0 group-hover:bg-slate-200/80 transition-colors">
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
      className={`border rounded-xl mb-3.5 overflow-hidden transition-all duration-300 bg-white group ${
        isExpanded
          ? 'border-slate-300 shadow-md ring-2 ring-slate-900/5'
          : 'border-slate-200/90 hover:border-slate-300 shadow-2xs hover:shadow-sm hover:-translate-y-0.5 cursor-pointer'
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
        className="p-3.5 sm:p-4 flex items-center justify-between cursor-pointer select-none bg-white hover:bg-slate-50/70 transition-colors duration-150 group"
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

          <div className="transition-transform duration-200 group-hover:scale-105">
            {getSectionIcon(section.type)}
          </div>

          <div className="flex items-center gap-1.5 min-w-0">
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
                  className="font-bold text-[15px] sm:text-[16px] text-slate-900 border border-blue-400 rounded px-2 py-0.5 focus:outline-none"
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
                <h3 className="font-bold text-[15px] sm:text-[16px] text-slate-900 tracking-tight truncate group-hover:text-blue-900 transition-colors">
                  {section.title}
                </h3>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditedTitle(section.title);
                    setIsEditingTitle(true);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-all cursor-pointer"
                  title="Rename section"
                >
                  <Edit2 className="w-3.5 h-3.5" />
                </button>
              </>
            )}
          </div>
        </div>

        {/* Right Actions & Chevron */}
        <div className="flex items-center gap-1.5 shrink-0" onClick={(e) => e.stopPropagation()}>
          {!section.visible && (
            <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-amber-50 text-amber-700 border border-amber-200/80">
              Hidden
            </span>
          )}

          <button
            type="button"
            onClick={() => toggleSectionVisibility(section.id)}
            aria-label={section.visible ? 'Hide section on resume' : 'Show section on resume'}
            className={`p-1.5 rounded-lg transition-all duration-150 cursor-pointer active:scale-95 ${
              section.visible
                ? 'opacity-0 group-hover:opacity-100 text-slate-400 hover:text-slate-800 hover:bg-slate-100'
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
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition-all duration-150 cursor-pointer active:scale-95"
          >
            <ChevronDown
              className={`w-4 h-4 transition-transform duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] ${
                isExpanded ? 'rotate-180' : ''
              }`}
            />
          </button>
        </div>
      </div>

      {/* Smooth Animated Stage Body */}
      <div
        className={`grid transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] ${
          isExpanded ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0 pointer-events-none'
        }`}
      >
        <div className="min-h-0 overflow-hidden">
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
              className="w-9 h-9 rounded-lg border border-slate-200 bg-white hover:bg-rose-50 hover:text-rose-600 hover:border-rose-200 text-slate-500 flex items-center justify-center transition-all duration-150 cursor-pointer active:scale-95"
              title="Delete Section"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
);
};

const AVAILABLE_SECTION_DEFS: {
  type: SectionType;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}[] = [
  { type: 'summary', label: 'Summary', icon: FileText },
  { type: 'experience', label: 'Work Experience', icon: Briefcase },
  { type: 'skills', label: 'Skills', icon: Lightbulb },
  { type: 'education', label: 'Education', icon: GraduationCap },
  { type: 'projects', label: 'Projects', icon: Folder },
  { type: 'certifications', label: 'Certifications', icon: Award },
  { type: 'languages', label: 'Languages', icon: Languages },
  { type: 'awards', label: 'Awards & Honors', icon: Award },
  { type: 'publications', label: 'Publications', icon: BookOpen },
  { type: 'volunteering', label: 'Volunteering', icon: HeartHandshake },
  { type: 'interests', label: 'Interests', icon: Compass },
  { type: 'references', label: 'References', icon: Users },
];

export const SectionList: React.FC = () => {
  const { content, reorderSections, addSection, activeSectionId, setActiveSectionId } =
    useResume();

  const [showAddMenu, setShowAddMenu] = useState(false);
  const [allCollapsed, setAllCollapsed] = useState(false);
  const [personalExpanded, setPersonalExpanded] = useState(true);

  // Set of section types already inserted in this resume (prevent duplicates)
  const existingTypes = new Set(content.sections.map((s) => s.type));

  // Filter available sections to ONLY include ones NOT already inserted
  const availableSections = AVAILABLE_SECTION_DEFS.filter(
    (def) => !existingTypes.has(def.type)
  );

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
      {/* Top Sub-bar / Stage Controls Filter Header with Glassmorphic Blur */}
      <div className="px-5 py-3 border-b border-slate-200/80 flex items-center justify-between bg-[#F8F9FA]/90 backdrop-blur-md sticky top-0 z-20 transition-all">
        <div className="flex items-center gap-2">
          <span className="font-bold text-sm text-slate-900">Resume Sections</span>
          <span className="px-2.5 py-0.5 rounded-full bg-white border border-slate-200/90 font-mono text-[11px] text-slate-700 font-semibold shadow-2xs flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            {activeSectionsCount} Active
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => setShowAddMenu((v) => !v)}
            className="inline-flex items-center gap-1 text-xs font-semibold text-[#FF2D6C] bg-pink-50 hover:bg-pink-100/80 border border-pink-200/80 transition-all cursor-pointer px-2.5 py-1 rounded-md active:scale-95 shadow-2xs"
            title="Add a new section"
          >
            <Plus className="w-3.5 h-3.5 stroke-[2.5]" />
            <span>Add Section</span>
          </button>
          <button
            type="button"
            onClick={handleToggleCollapseAll}
            className="text-xs font-medium text-slate-600 hover:text-slate-900 transition-all cursor-pointer px-2.5 py-1 rounded-md hover:bg-white hover:shadow-2xs active:scale-95"
            title={allCollapsed ? 'Expand all sections' : 'Collapse all sections'}
          >
            {allCollapsed ? 'Expand All' : 'Collapse All'}
          </button>
          <button
            type="button"
            className="p-1.5 rounded-md text-slate-400 hover:text-slate-700 hover:bg-white hover:shadow-2xs active:scale-95 transition-all cursor-pointer"
            title="Reorder sections"
          >
            <ArrowUpDown className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Subtle top scroll gradient shadow */}
      <div className="h-4 bg-gradient-to-b from-slate-200/30 to-transparent sticky top-[49px] z-10 -mb-4 pointer-events-none" />

      {/* Scrollable Stage Cards Container with Smooth Scroll */}
      <div id="resume-sections-scroll-container" className="flex-1 overflow-y-auto custom-scrollbar scroll-smooth p-4 sm:p-5 pb-12">
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

        {/* + Add Content Button Placed Cleanly Below Sections (Never Covering Any Card) */}
        <div className="pt-3 pb-32 flex items-center justify-start">
          <button
            type="button"
            onClick={() => setShowAddMenu((v) => !v)}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#FF2D6C] to-[#FF5E62] text-white font-bold text-sm shadow-[0_4px_16px_rgba(255,45,108,0.35)] animate-cta-breath hover:scale-[1.03] active:scale-[0.97] transition-all duration-200 cursor-pointer select-none"
          >
            <Plus className="w-4 h-4 stroke-[2.5]" />
            <span>Add Content</span>
          </button>
        </div>
      </div>

      {/* Popup 2-Column Menu for Adding Sections */}
      {showAddMenu && (
        <>
          <div
            className="fixed inset-0 z-35 bg-black/10 backdrop-blur-[1px]"
            onClick={() => setShowAddMenu(false)}
          />
          <div className="absolute bottom-16 left-4 right-4 sm:left-5 sm:right-5 bg-white/98 backdrop-blur-md rounded-2xl border border-slate-200 shadow-2xl p-4 z-40 animate-modal-pop">
            <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-200/80">
              <div>
                <span className="font-bold text-sm text-slate-900 block">Add Resume Section</span>
                <span className="text-xs text-slate-500">
                  {availableSections.length > 0
                    ? 'Choose an unadded section to append to your resume'
                    : 'All standard sections have been added to your resume'}
                </span>
              </div>
              <button
                type="button"
                onClick={() => setShowAddMenu(false)}
                className="w-6 h-6 rounded-full hover:bg-slate-100 flex items-center justify-center text-slate-400 hover:text-slate-800 transition-colors cursor-pointer"
              >
                ×
              </button>
            </div>

            {availableSections.length > 0 ? (
              <div className="grid grid-cols-2 gap-2 text-left mb-2.5 max-h-56 overflow-y-auto custom-scrollbar pr-1">
                {availableSections.map((sec) => {
                  const Icon = sec.icon;
                  return (
                    <button
                      key={sec.type}
                      type="button"
                      onClick={() => handleAdd(sec.type)}
                      className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-slate-100/80 text-slate-800 text-xs font-medium border border-transparent hover:border-slate-200 hover:translate-x-0.5 active:scale-[0.99] transition-all cursor-pointer"
                    >
                      <Icon className="w-4 h-4 text-slate-800 shrink-0" />
                      <span className="truncate">{sec.label}</span>
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="py-3 px-2 text-center text-xs text-slate-500 bg-slate-50 rounded-xl mb-2.5">
                All standard sections are currently in your resume.
              </div>
            )}

            <button
              type="button"
              onClick={() => handleAdd('custom')}
              className="w-full flex items-center justify-center gap-2 p-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold border border-slate-200 active:scale-[0.99] transition-all cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>+ Custom Section</span>
            </button>
          </div>
        </>
      )}
    </div>
  );
};

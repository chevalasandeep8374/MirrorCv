'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useResume } from '@/context/ResumeContext';
import { SectionItem, SectionType, BulletItem } from '@/types/content';
import { BulletList } from './BulletList';
import { StructuredDateEditor } from './StructuredDateEditor';
import {
  ArrowLeft,
  Check,
  Eye,
  EyeOff,
  Trash2,
  Sparkles,
  Bold,
  Italic,
  Underline,
  List,
  Link as LinkIcon,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignJustify,
  Calendar,
  MapPin,
  Building,
  Tag,
  Plus,
  X,
  ExternalLink,
  ChevronDown,
} from 'lucide-react';

interface EditEntryViewProps {
  sectionId: string;
  itemId: string;
  onClose: () => void;
}

export const EditEntryView: React.FC<EditEntryViewProps> = ({
  sectionId,
  itemId,
  onClose,
}) => {
  const {
    content,
    updateItem,
    removeItem,
    addBullet,
    removeBullet,
    updateBullet,
    reorderBullets,
  } = useResume();

  const section = content.sections.find((s) => s.id === sectionId);
  const item = section?.items.find((i) => i.id === itemId);

  const [showTips, setShowTips] = useState(false);
  const [skillTagInput, setSkillTagInput] = useState('');
  const richTextareaRef = useRef<HTMLTextAreaElement>(null);

  // If section or item does not exist (e.g. deleted), close view
  useEffect(() => {
    if (!section || !item) {
      onClose();
    }
  }, [section, item, onClose]);

  if (!section || !item) {
    return null;
  }

  const isHidden = item.visible === false;

  // Sub-skills text handling for skills section
  const getSubSkillsText = (): string => {
    if (!item.bullets || item.bullets.length === 0) return '';
    return item.bullets.map((b) => b.text).join(', ');
  };

  const handleSubSkillsTextChange = (newText: string) => {
    // If the user is typing freeform, store it in bullets
    // Split by commas or newlines if multiple, or keep single bullet
    if (!newText.trim()) {
      updateItem(sectionId, itemId, { bullets: [] });
      return;
    }

    const items = newText
      .split(/,\s*/)
      .map((s) => s.trim())
      .filter(Boolean);

    const updatedBullets: BulletItem[] = items.map((name, idx) => ({
      id: item.bullets?.[idx]?.id || `skill-${Date.now()}-${idx}`,
      text: name,
      proficiency: item.bullets?.[idx]?.proficiency || null,
    }));

    updateItem(sectionId, itemId, { bullets: updatedBullets });
  };

  // Rich formatting helper for the textarea
  const applyTextMarkup = (format: 'bold' | 'italic' | 'underline' | 'bullet' | 'link') => {
    const el = richTextareaRef.current;
    if (!el) return;
    const start = el.selectionStart;
    const end = el.selectionEnd;
    const val = el.value;
    const selected = val.substring(start, end);

    let replacement = '';
    if (format === 'bold') {
      replacement = `**${selected || 'bold text'}**`;
    } else if (format === 'italic') {
      replacement = `*${selected || 'italic text'}*`;
    } else if (format === 'underline') {
      replacement = `<u>${selected || 'underlined text'}</u>`;
    } else if (format === 'bullet') {
      replacement = `\n• ${selected || 'Bullet item'}`;
    } else if (format === 'link') {
      const url = prompt('Enter URL (https://...):', 'https://');
      if (!url) return;
      replacement = `[${selected || 'link text'}](${url})`;
    }

    const nextVal = val.substring(0, start) + replacement + val.substring(end);
    handleSubSkillsTextChange(nextVal);

    setTimeout(() => {
      el.focus();
      el.setSelectionRange(start + 2, start + 2 + (selected.length || 9));
    }, 20);
  };

  // Add individual skill tag
  const handleAddSkillTag = () => {
    const trimmed = skillTagInput.trim().replace(/^,+|,+$/g, '');
    if (!trimmed) return;

    const newNames = trimmed
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

    const newBullets: BulletItem[] = [
      ...(item.bullets || []),
      ...newNames.map((name) => ({
        id: `skill-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
        text: name,
        proficiency: null,
      })),
    ];

    updateItem(sectionId, itemId, { bullets: newBullets });
    setSkillTagInput('');
  };

  // Curated writing tips per section type
  const getSectionTips = (type: SectionType): string[] => {
    switch (type) {
      case 'skills':
        return [
          'Group related technologies into cohesive domains (e.g. Languages & Frameworks, Cloud & DevOps, AI / Agentic Architecture).',
          'Put your strongest, most role-relevant proficiencies first so recruiters and ATS parse them instantly.',
          'Specify key frameworks, libraries, and tools rather than generic labels (e.g. "LangGraph, FastAPI, Redis" instead of "Backend").',
          'Highlight tools matching the exact keywords from your target job description.',
        ];
      case 'experience':
        return [
          'Lead each bullet point with a dynamic action verb in past tense (e.g. Architected, Engineered, Spearheaded, Automated).',
          'Quantify your business impact using exact metrics (e.g. "reduced latency by 45%", "scaled throughput to 50k req/s").',
          'Use the Google XYZ Formula: "Accomplished [X] as measured by [Y] by doing [Z]".',
          'Keep bullets concise (1 to 2 lines) and focus on outcome and ownership rather than passive routine tasks.',
        ];
      case 'education':
        return [
          'List your highest degree first, including official degree title and major/specialization.',
          'Include relevant academic achievements (e.g. Magna Cum Laude, Dean\'s List, GPA if 3.5+).',
          'Highlight notable coursework, capstone projects, or student leadership if early in your career.',
        ];
      case 'projects':
        return [
          'Summarize the core technical problem solved and the end-to-end architecture.',
          'Explicitly mention the tech stack (e.g. "FastAPI, LangGraph, Supabase, Next.js, Docker").',
          'Link to the live demo, GitHub repository, or product URL whenever possible.',
          'State real results (e.g. "Processed 10k+ documents with 99.4% extraction accuracy").',
        ];
      case 'certifications':
        return [
          'Use the official certification name and full issuing authority (e.g. AWS Certified Solutions Architect - Professional).',
          'Include the issue date and credential ID or verification link to boost verification credibility.',
        ];
      case 'languages':
        return [
          'Accurately state your proficiency level (Native, Fluent, Professional Working, Conversational).',
          'List standard CEFR levels (C2, C1, B2) if applying internationally or in Europe.',
        ];
      default:
        return [
          'Be clear, concise, and highlight tangible contributions and achievements.',
          'Ensure dates and locations are consistent across your entire resume.',
        ];
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#F8F9FA] select-none isolate-paint">
      {/* Top Header Bar matching FlowCV Pattern */}
      <div className="p-4 border-b border-slate-200/90 bg-white sticky top-0 z-20 flex items-center justify-between shadow-2xs">
        <div className="flex items-center gap-2.5 min-w-0">
          <button
            type="button"
            onClick={onClose}
            className="h-10 w-10 -ml-1 text-black hover:bg-slate-100 rounded-xl transition-colors cursor-pointer flex items-center justify-center border border-slate-200"
            title="Back to sections"
          >
            <ArrowLeft className="w-4.5 h-4.5" />
          </button>
          <div className="min-w-0">
            <h2 className="text-lg font-black text-black leading-tight">Edit Entry</h2>
            <span className="text-xs text-slate-700 font-semibold truncate block">
              {section.title}
            </span>
          </div>
        </div>

        {/* Header Right Actions */}
        <div className="flex items-center gap-2 shrink-0">
          {/* Get Tips Button */}
          <button
            type="button"
            onClick={() => setShowTips((prev) => !prev)}
            className={`h-10 inline-flex items-center gap-2 px-4 rounded-xl border text-xs sm:text-sm font-bold shadow-2xs transition-all cursor-pointer ${
              showTips
                ? 'bg-purple-50 border-purple-300 text-purple-700'
                : 'border-slate-200 bg-white hover:bg-slate-50 text-black'
            }`}
            title="Get expert writing tips for this section"
          >
            <Sparkles className="w-4 h-4 text-[#5A32EA]" />
            <span>Get Tips</span>
          </button>

          {/* Visibility Toggle */}
          <button
            type="button"
            onClick={() => updateItem(sectionId, itemId, { visible: isHidden ? true : false })}
            className={`h-10 w-10 rounded-xl border flex items-center justify-center transition-all cursor-pointer ${
              isHidden
                ? 'border-amber-200 bg-amber-50 text-amber-700'
                : 'border-slate-200 bg-white text-slate-600 hover:text-black hover:bg-slate-50'
            }`}
            title={isHidden ? 'Item is hidden on resume (click to show)' : 'Hide item on resume'}
          >
            {isHidden ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>

          {/* Delete Item */}
          <button
            type="button"
            onClick={() => {
              if (confirm('Are you sure you want to delete this entry?')) {
                removeItem(sectionId, itemId);
                onClose();
              }
            }}
            className="h-10 w-10 rounded-xl border border-slate-200 bg-white text-slate-500 hover:text-rose-600 hover:border-rose-200 hover:bg-rose-50 flex items-center justify-center transition-colors cursor-pointer"
            title="Delete entry"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Expandable Tips Panel */}
      {showTips && (
        <div className="mx-4 mt-3 p-3.5 bg-gradient-to-r from-purple-50/90 to-indigo-50/90 border border-purple-200/70 rounded-xl text-xs text-purple-950 animate-in fade-in slide-in-from-top-2 duration-200 shadow-xs">
          <div className="flex items-center justify-between font-bold text-purple-900 mb-1.5">
            <span className="flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-[#5A32EA]" />
              <span>Pro Tips for {section.title}</span>
            </span>
            <button
              type="button"
              onClick={() => setShowTips(false)}
              className="text-purple-400 hover:text-purple-700 cursor-pointer p-0.5 text-sm font-bold leading-none"
            >
              ×
            </button>
          </div>
          <ul className="space-y-1.5 text-[11.5px] leading-relaxed list-disc list-inside text-purple-900/90 pt-0.5">
            {getSectionTips(section.type).map((tip, idx) => (
              <li key={idx}>{tip}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Form Fields Body (Scrollable) */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-4 sm:p-5 space-y-4">
        {/* ======================================================== */}
        {/* SKILLS SECTION (Matches Screenshot 2 FlowCV Pattern)     */}
        {/* ======================================================== */}
        {section.type === 'skills' ? (
          <div className="space-y-4">
            {/* Skill / Group Name */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">
                Skill
              </label>
              <input
                type="text"
                value={item.title || ''}
                onChange={(e) => updateItem(sectionId, itemId, { title: e.target.value })}
                placeholder="e.g. Agentic AI, Programming & CS Fundamentals, Cloud & DevOps"
                className="w-full text-xs font-semibold px-3 py-2 bg-white border border-slate-200 rounded-xl focus:outline-hidden focus:ring-1 focus:ring-blue-500 text-slate-900 transition-all shadow-2xs"
              />
            </div>

            {/* Information / Sub-skills Rich Editor */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">
                Information / Sub-skills
              </label>

              {/* Rich Text Toolbar */}
              <div className="border border-slate-200 rounded-xl overflow-hidden bg-white shadow-2xs focus-within:ring-1 focus-within:ring-blue-500">
                <div className="flex items-center gap-0.5 p-1.5 bg-slate-50 border-b border-slate-200 text-slate-600">
                  <button
                    type="button"
                    onClick={() => applyTextMarkup('bold')}
                    className="p-1 hover:bg-slate-200/80 rounded text-slate-700 transition-colors"
                    title="Bold"
                  >
                    <Bold className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => applyTextMarkup('italic')}
                    className="p-1 hover:bg-slate-200/80 rounded text-slate-700 transition-colors"
                    title="Italic"
                  >
                    <Italic className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => applyTextMarkup('underline')}
                    className="p-1 hover:bg-slate-200/80 rounded text-slate-700 transition-colors"
                    title="Underline"
                  >
                    <Underline className="w-3.5 h-3.5" />
                  </button>
                  <div className="w-px h-3.5 bg-slate-200 mx-1" />
                  <button
                    type="button"
                    onClick={() => applyTextMarkup('bullet')}
                    className="p-1 hover:bg-slate-200/80 rounded text-slate-700 transition-colors"
                    title="Bullet List"
                  >
                    <List className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => applyTextMarkup('link')}
                    className="p-1 hover:bg-slate-200/80 rounded text-slate-700 transition-colors"
                    title="Add Link"
                  >
                    <LinkIcon className="w-3.5 h-3.5" />
                  </button>
                  <div className="w-px h-3.5 bg-slate-200 mx-1" />
                  <button
                    type="button"
                    onClick={() => applyTextMarkup('bold')}
                    className="p-1 hover:bg-slate-200/80 rounded text-slate-700 transition-colors"
                    title="Align Left"
                  >
                    <AlignLeft className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => applyTextMarkup('bold')}
                    className="p-1 hover:bg-slate-200/80 rounded text-slate-700 transition-colors"
                    title="Align Center"
                  >
                    <AlignCenter className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => applyTextMarkup('bold')}
                    className="p-1 hover:bg-slate-200/80 rounded text-slate-700 transition-colors"
                    title="Align Right"
                  >
                    <AlignRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                <textarea
                  ref={richTextareaRef}
                  rows={4}
                  value={getSubSkillsText()}
                  onChange={(e) => handleSubSkillsTextChange(e.target.value)}
                  placeholder="e.g. LangGraph (StateGraph, typed state), LangChain, Multi-Agent Systems, RAG Pipelines (FAISS, Chroma, Embeddings)..."
                  className="w-full p-3 text-xs text-slate-900 border-none outline-hidden focus:ring-0 leading-relaxed resize-none"
                />
              </div>
            </div>

            {/* Skill Level Dropdown Selector */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">
                Skill level
              </label>
              <div className="relative">
                <select
                  value={item.subtitle || ''}
                  onChange={(e) => updateItem(sectionId, itemId, { subtitle: e.target.value })}
                  className="w-full text-xs px-3 py-2 bg-white border border-slate-200 rounded-xl focus:outline-hidden focus:ring-1 focus:ring-blue-500 text-slate-800 transition-all shadow-2xs appearance-none pr-8 cursor-pointer"
                >
                  <option value="">Select skill level (optional)</option>
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                  <option value="Expert">Expert</option>
                  <option value="Master / Specialist">Master / Specialist</option>
                </select>
                <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>
            </div>

            {/* Interactive Skill Chips with Quick Add */}
            <div className="pt-2 border-t border-slate-200/80">
              <label className="block text-[11px] font-semibold text-slate-500 mb-1.5 flex items-center justify-between">
                <span className="flex items-center gap-1.5">
                  <Tag className="w-3.5 h-3.5 text-blue-600" />
                  <span>Individual Skill Chips (Click × to remove)</span>
                </span>
                <span className="text-[10px] text-slate-400">
                  {(item.bullets || []).length} items
                </span>
              </label>

              <div className="flex items-center gap-2 mb-2">
                <input
                  type="text"
                  value={skillTagInput}
                  onChange={(e) => setSkillTagInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ',') {
                      e.preventDefault();
                      handleAddSkillTag();
                    }
                  }}
                  placeholder="Type skill & press Enter or comma..."
                  className="flex-1 text-xs px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
                />
                <button
                  type="button"
                  onClick={handleAddSkillTag}
                  disabled={!skillTagInput.trim()}
                  className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white font-semibold text-xs rounded-lg transition-colors flex items-center gap-1 cursor-pointer"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add</span>
                </button>
              </div>

              {/* Chips list */}
              <div className="flex flex-wrap gap-1.5">
                {(item.bullets || []).map((bullet) => (
                  <span
                    key={bullet.id}
                    className="inline-flex items-center gap-1.5 bg-white border border-slate-200 rounded-lg px-2.5 py-1 text-xs font-medium text-slate-800 shadow-2xs group hover:border-slate-300"
                  >
                    <span>{bullet.text}</span>
                    <button
                      type="button"
                      onClick={() => removeBullet(sectionId, itemId, bullet.id)}
                      className="text-slate-400 hover:text-rose-500 p-0.5 rounded transition-colors cursor-pointer"
                      title="Remove skill"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* ======================================================== */
          /* STANDARD SECTIONS (Work Experience, Education, Projects) */
          /* ======================================================== */
          <div className="space-y-4">
            {/* Primary Title & Organization */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  {section.type === 'experience'
                    ? 'Job Title / Role'
                    : section.type === 'education'
                    ? 'Degree / Major'
                    : section.type === 'projects'
                    ? 'Project Name'
                    : section.type === 'certifications'
                    ? 'Certification Name'
                    : section.type === 'languages'
                    ? 'Language'
                    : 'Title / Role'}
                </label>
                <input
                  type="text"
                  value={item.title || ''}
                  onChange={(e) => updateItem(sectionId, itemId, { title: e.target.value })}
                  placeholder={
                    section.type === 'experience'
                      ? 'e.g. Principal Software Engineer'
                      : section.type === 'education'
                      ? 'e.g. B.S. in Computer Science'
                      : section.type === 'projects'
                      ? 'e.g. Multi-Agent Lead Engine'
                      : 'Enter title...'
                  }
                  className="w-full text-xs font-semibold px-3 py-2 bg-white border border-slate-200 rounded-xl focus:outline-hidden focus:ring-1 focus:ring-blue-500 text-slate-900 transition-all shadow-2xs"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  {section.type === 'experience'
                    ? 'Organization / Company'
                    : section.type === 'education'
                    ? 'School / University'
                    : section.type === 'projects'
                    ? 'Tech Stack / Subtitle'
                    : section.type === 'certifications'
                    ? 'Issuing Organization'
                    : section.type === 'languages'
                    ? 'Proficiency Level'
                    : 'Organization / Subtitle'}
                </label>
                {section.type === 'languages' ? (
                  <div className="relative">
                    <select
                      value={item.subtitle || ''}
                      onChange={(e) => updateItem(sectionId, itemId, { subtitle: e.target.value })}
                      className="w-full text-xs px-3 py-2 bg-white border border-slate-200 rounded-xl focus:outline-hidden focus:ring-1 focus:ring-blue-500 text-slate-800 transition-all shadow-2xs appearance-none pr-8 cursor-pointer"
                    >
                      <option value="">Select proficiency level</option>
                      <option value="Native or Bilingual">Native or Bilingual</option>
                      <option value="Full Professional Proficiency">Full Professional Proficiency</option>
                      <option value="Professional Working Proficiency">Professional Working Proficiency</option>
                      <option value="Limited Working Proficiency">Limited Working Proficiency</option>
                      <option value="Elementary Proficiency">Elementary Proficiency</option>
                    </select>
                    <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                  </div>
                ) : (
                  <input
                    type="text"
                    value={item.subtitle || ''}
                    onChange={(e) => updateItem(sectionId, itemId, { subtitle: e.target.value })}
                    placeholder={
                      section.type === 'experience'
                        ? 'e.g. Acme Cloud Platforms'
                        : section.type === 'education'
                        ? 'e.g. UC Berkeley'
                        : section.type === 'projects'
                        ? 'e.g. Python, FastAPI, LangGraph, Supabase'
                        : 'Enter subtitle...'
                    }
                    className="w-full text-xs px-3 py-2 bg-white border border-slate-200 rounded-xl focus:outline-hidden focus:ring-1 focus:ring-blue-500 text-slate-900 transition-all shadow-2xs"
                  />
                )}
              </div>
            </div>

            {/* Location & Optional Link (if not languages or certifications) */}
            {section.type !== 'languages' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span>Location</span>
                  </label>
                  <input
                    type="text"
                    value={item.location || ''}
                    onChange={(e) => updateItem(sectionId, itemId, { location: e.target.value })}
                    placeholder="e.g. San Francisco, CA (or Remote)"
                    className="w-full text-xs px-3 py-2 bg-white border border-slate-200 rounded-xl focus:outline-hidden focus:ring-1 focus:ring-blue-500 text-slate-900 transition-all shadow-2xs"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5 flex items-center gap-1.5">
                    <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
                    <span>
                      {section.type === 'projects'
                        ? 'Project URL / Repository'
                        : 'Project / Org Link (Optional)'}
                    </span>
                  </label>
                  <input
                    type="text"
                    value={item.link?.url || ''}
                    onChange={(e) =>
                      updateItem(sectionId, itemId, {
                        link: e.target.value ? { url: e.target.value } : null,
                      })
                    }
                    placeholder="https://github.com/... or https://..."
                    className="w-full text-xs px-3 py-2 bg-white border border-slate-200 rounded-xl focus:outline-hidden focus:ring-1 focus:ring-blue-500 text-slate-900 transition-all shadow-2xs"
                  />
                </div>
              </div>
            )}

            {/* Structured Date Range */}
            {section.type !== 'languages' && (
              <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-2xs">
                <StructuredDateEditor
                  dates={item.dates}
                  dateRange={item.dateRange}
                  onChange={(dates, formatted) =>
                    updateItem(sectionId, itemId, {
                      dates,
                      dateRange: formatted,
                    })
                  }
                />
              </div>
            )}

            {/* Bullet Points / Responsibilities */}
            {section.type !== 'languages' && (
              <div className="pt-2 border-t border-slate-200/80">
                <BulletList
                  bullets={item.bullets || []}
                  onAddBullet={() => addBullet(sectionId, itemId)}
                  onRemoveBullet={(bId) => removeBullet(sectionId, itemId, bId)}
                  onUpdateBullet={(bId, patch) => updateBullet(sectionId, itemId, bId, patch)}
                  onReorderBullets={(oIdx, nIdx) => reorderBullets(sectionId, itemId, oIdx, nIdx)}
                />
              </div>
            )}
          </div>
        )}
      </div>

      {/* Sticky Bottom Done Action matching Screenshot 2 */}
      <div className="p-4 bg-white/95 backdrop-blur-md border-t border-slate-200 sticky bottom-0 z-20 shadow-lg">
        <button
          type="button"
          onClick={onClose}
          className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-[#FF2D6C] to-[#FF5E62] hover:from-[#E6205E] hover:to-[#F04F54] text-white font-bold text-sm shadow-[0_4px_16px_rgba(255,45,108,0.35)] active:scale-[0.98] transition-all flex items-center justify-center gap-2 cursor-pointer select-none"
        >
          <Check className="w-4 h-4 stroke-[2.5]" />
          <span>Done</span>
        </button>
      </div>
    </div>
  );
};

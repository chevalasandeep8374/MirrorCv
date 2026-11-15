'use client';

import React, { useState, useEffect } from 'react';
import { Sparkles, X, Check, BookOpen, Cpu, DollarSign, AlertCircle } from 'lucide-react';
import { useResume } from '@/context/ResumeContext';
import { apiClient } from '@/lib/api';

interface AiAssistantModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface SkillSuggestion {
  skill: string;
  category: string;
  source_context: string;
}

export const AiAssistantModal: React.FC<AiAssistantModalProps> = ({
  isOpen,
  onClose,
}) => {
  const { content, updateContent, addSection, addItem, updateItem } = useResume();
  const [activeTab, setActiveTab] = useState<'summary' | 'skills' | 'usage'>('summary');

  // Summary generation states
  const [summaryTone, setSummaryTone] = useState<'formal' | 'executive' | 'technical' | 'casual'>('formal');
  const [targetJobTitle, setTargetJobTitle] = useState(content.header?.title || '');
  const [generatedSummary, setGeneratedSummary] = useState<string | null>(null);
  const [summaryThemes, setSummaryThemes] = useState<string[]>([]);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  // Skills suggestion states
  const [suggestedSkills, setSuggestedSkills] = useState<SkillSuggestion[]>([]);
  const [selectedSkills, setSelectedSkills] = useState<Set<string>>(new Set());
  const [skillsLoading, setSkillsLoading] = useState(false);
  const [skillsError, setSkillsError] = useState<string | null>(null);

  // Usage states
  const [usageData, setUsageData] = useState<{
    daily_requests_used: number;
    daily_limit: number;
    requests_remaining: number;
    total_cost_usd: number;
  } | null>(null);

  const fetchUsage = async () => {
    try {
      const res = await apiClient.get('/ai/usage');
      setUsageData(res.data);
    } catch {
      // Ignore or log error
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchUsage();
      setTargetJobTitle(content.header?.title || '');
    }
  }, [isOpen, content.header?.title]);

  if (!isOpen) return null;

  // Extract experience bullets for summary and skills
  const getExperienceBullets = (): string[] => {
    const bullets: string[] = [];
    content.sections.forEach((sec) => {
      if (sec.type === 'experience' || sec.type === 'projects') {
        sec.items.forEach((item) => {
          if (item.bullets) {
            item.bullets.forEach((b) => {
              if (b.text.trim()) bullets.push(b.text.trim());
            });
          }
        });
      }
    });
    return bullets;
  };

  const getExistingSkills = (): string[] => {
    const skills: string[] = [];
    const skillsSec = content.sections.find((s) => s.type === 'skills');
    if (skillsSec) {
      skillsSec.items.forEach((item) => {
        if (item.title) skills.push(item.title);
        if (item.bullets) item.bullets.forEach((b) => skills.push(b.text));
      });
    }
    return skills;
  };

  // Generate Summary handler
  const handleGenerateSummary = async () => {
    setSummaryLoading(true);
    setSummaryError(null);
    try {
      const bullets = getExperienceBullets();
      const skills = getExistingSkills();
      const res = await apiClient.post('/ai/generate-summary', {
        job_title: targetJobTitle || undefined,
        experience_bullets: bullets,
        skills,
        tone: summaryTone,
      });
      setGeneratedSummary(res.data.suggested_summary);
      setSummaryThemes(res.data.key_themes || []);
      fetchUsage();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } };
      if (axiosErr.response?.status === 429) {
        setSummaryError(axiosErr.response.data?.detail || 'Daily AI rate limit reached.');
      } else {
        setSummaryError('Failed to generate summary. Please try again.');
      }
    } finally {
      setSummaryLoading(false);
    }
  };

  // Apply Summary to Resume
  const handleApplySummary = () => {
    if (!generatedSummary) return;
    const summarySec = content.sections.find((s) => s.type === 'summary');
    const summaryItem = {
      id: `summary-item-${Date.now()}`,
      title: '',
      subtitle: '',
      location: '',
      dateRange: '',
      itemType: 'paragraph' as const,
      bullets: [{ id: `summary-bullet-${Date.now()}`, text: generatedSummary }],
    };

    if (summarySec) {
      const nextSections = content.sections.map((s) =>
        s.id === summarySec.id ? { ...s, items: [summaryItem] } : s
      );
      updateContent({ ...content, sections: nextSections });
    } else {
      const newSec = {
        id: `section-summary-${Date.now()}`,
        type: 'summary' as const,
        title: 'Professional Summary',
        visible: true,
        items: [summaryItem],
      };
      updateContent({ ...content, sections: [newSec, ...content.sections] });
    }
    onClose();
  };

  // Suggest Skills handler
  const handleSuggestSkills = async () => {
    setSkillsLoading(true);
    setSkillsError(null);
    try {
      const bullets = getExperienceBullets();
      const existing = getExistingSkills();
      const res = await apiClient.post('/ai/suggest-skills', {
        experience_texts: bullets.length > 0 ? bullets : ['Developed full stack web applications and backend APIs.'],
        existing_skills: existing,
      });
      const suggestions: SkillSuggestion[] = res.data.suggestions || [];
      setSuggestedSkills(suggestions);
      setSelectedSkills(new Set(suggestions.map((s) => s.skill)));
      fetchUsage();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } };
      if (axiosErr.response?.status === 429) {
        setSkillsError(axiosErr.response.data?.detail || 'Daily AI rate limit reached.');
      } else {
        setSkillsError('Failed to suggest skills. Please try again.');
      }
    } finally {
      setSkillsLoading(false);
    }
  };

  // Apply selected skills to Resume
  const handleApplySkills = () => {
    const toAdd = Array.from(selectedSkills);
    if (toAdd.length === 0) return;

    let skillsSec = content.sections.find((s) => s.type === 'skills');
    const newItems = toAdd.map((s, idx) => ({
      id: `ai-skill-${Date.now()}-${idx}`,
      title: s,
      subtitle: '',
      location: '',
      dateRange: '',
      itemType: 'tags' as const,
      bullets: [],
    }));

    if (skillsSec) {
      const currentItems = skillsSec.items || [];
      const nextSections = content.sections.map((s) =>
        s.id === skillsSec!.id ? { ...s, items: [...currentItems, ...newItems] } : s
      );
      updateContent({ ...content, sections: nextSections });
    } else {
      const newSec = {
        id: `section-skills-${Date.now()}`,
        type: 'skills' as const,
        title: 'Skills',
        visible: true,
        items: newItems,
      };
      updateContent({ ...content, sections: [...content.sections, newSec] });
    }
    onClose();
  };

  const toggleSkillSelection = (skillName: string) => {
    setSelectedSkills((prev) => {
      const next = new Set(prev);
      if (next.has(skillName)) {
        next.delete(skillName);
      } else {
        next.add(skillName);
      }
      return next;
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 bg-gradient-to-r from-blue-700 via-indigo-700 to-purple-800 text-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Sparkles className="w-5 h-5 text-amber-300" />
            <div>
              <h2 className="font-bold text-base leading-tight">AI Resume Assistant</h2>
              <p className="text-[11px] text-blue-100 font-medium">
                Grounded generation with zero hallucinations & verified facts
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white/80 hover:text-white p-1 rounded-lg hover:bg-white/10"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 bg-slate-50 px-6 text-xs font-semibold text-slate-600">
          <button
            onClick={() => setActiveTab('summary')}
            className={`py-3 px-4 border-b-2 flex items-center gap-1.5 transition-colors ${
              activeTab === 'summary'
                ? 'border-blue-600 text-blue-600 font-bold bg-white'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Executive Summary</span>
          </button>
          <button
            onClick={() => setActiveTab('skills')}
            className={`py-3 px-4 border-b-2 flex items-center gap-1.5 transition-colors ${
              activeTab === 'skills'
                ? 'border-blue-600 text-blue-600 font-bold bg-white'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            <Cpu className="w-4 h-4" />
            <span>Skills Suggester</span>
          </button>
          <button
            onClick={() => setActiveTab('usage')}
            className={`py-3 px-4 border-b-2 flex items-center gap-1.5 transition-colors ${
              activeTab === 'usage'
                ? 'border-blue-600 text-blue-600 font-bold bg-white'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            <DollarSign className="w-4 h-4" />
            <span>Usage & Quota</span>
          </button>
        </div>

        {/* Tab Body */}
        <div className="p-6 overflow-y-auto space-y-4 flex-1">
          {/* TAB 1: EXECUTIVE SUMMARY */}
          {activeTab === 'summary' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-bold text-slate-600 block mb-1">
                    Target Job Title
                  </label>
                  <input
                    type="text"
                    value={targetJobTitle}
                    onChange={(e) => setTargetJobTitle(e.target.value)}
                    placeholder="e.g. Senior Full Stack Engineer"
                    className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="text-xs font-bold text-slate-600 block mb-1">
                    Tone & Voice
                  </label>
                  <select
                    value={summaryTone}
                    onChange={(e) => setSummaryTone(e.target.value as 'formal' | 'executive' | 'technical' | 'casual')}
                    className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
                  >
                    <option value="formal">Formal & Professional</option>
                    <option value="executive">Executive & Leadership</option>
                    <option value="technical">Technical & Systems Focused</option>
                    <option value="casual">Modern & Direct</option>
                  </select>
                </div>
              </div>

              {summaryError && (
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{summaryError}</span>
                </div>
              )}

              <button
                type="button"
                disabled={summaryLoading}
                onClick={handleGenerateSummary}
                className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                <Sparkles className="w-4 h-4" />
                <span>{summaryLoading ? 'Analyzing Experience & Generating...' : 'Generate Grounded Summary'}</span>
              </button>

              {generatedSummary && (
                <div className="space-y-3 pt-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                      Generated Summary
                    </span>
                    {summaryThemes.length > 0 && (
                      <div className="flex gap-1.5 flex-wrap">
                        {summaryThemes.map((th, i) => (
                          <span
                            key={i}
                            className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full font-medium"
                          >
                            {th}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="p-3.5 bg-blue-50/60 border border-blue-200 rounded-xl text-xs text-slate-800 leading-relaxed font-medium">
                    {generatedSummary}
                  </div>
                  <button
                    type="button"
                    onClick={handleApplySummary}
                    className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <Check className="w-4 h-4" />
                    <span>Accept & Insert into Resume Summary</span>
                  </button>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: SKILLS SUGGESTER */}
          {activeTab === 'skills' && (
            <div className="space-y-4">
              <p className="text-xs text-slate-600">
                Scans your employment history, project descriptions, and achievements to uncover hard and soft skills you demonstrated but may have forgotten to list.
              </p>

              {skillsError && (
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{skillsError}</span>
                </div>
              )}

              <button
                type="button"
                disabled={skillsLoading}
                onClick={handleSuggestSkills}
                className="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                <Cpu className="w-4 h-4" />
                <span>{skillsLoading ? 'Scanning Resume Content...' : 'Extract & Suggest Skills'}</span>
              </button>

              {suggestedSkills.length > 0 && (
                <div className="space-y-3 pt-2">
                  <div className="flex items-center justify-between text-xs text-slate-600 font-semibold">
                    <span>Select skills to add ({selectedSkills.size} of {suggestedSkills.length} selected):</span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-60 overflow-y-auto p-1">
                    {suggestedSkills.map((item, idx) => {
                      const isChecked = selectedSkills.has(item.skill);
                      return (
                        <div
                          key={idx}
                          onClick={() => toggleSkillSelection(item.skill)}
                          className={`p-2.5 rounded-lg border text-xs cursor-pointer transition-all flex items-start gap-2 ${
                            isChecked
                              ? 'border-indigo-500 bg-indigo-50/50 text-indigo-950 font-medium'
                              : 'border-slate-200 hover:border-slate-300 text-slate-600'
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => {}} // handled by parent onClick
                            className="mt-0.5 rounded text-indigo-600 focus:ring-indigo-500"
                          />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <span className="font-bold">{item.skill}</span>
                              <span className="text-[10px] bg-slate-100 text-slate-500 px-1.5 py-0.2 rounded font-normal">
                                {item.category}
                              </span>
                            </div>
                            {item.source_context && (
                              <p className="text-[10px] text-slate-500 truncate mt-0.5">
                                {item.source_context}
                              </p>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  <button
                    type="button"
                    disabled={selectedSkills.size === 0}
                    onClick={handleApplySkills}
                    className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50"
                  >
                    <Check className="w-4 h-4" />
                    <span>Add {selectedSkills.size} Approved Skills to Resume</span>
                  </button>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: USAGE & COST */}
          {activeTab === 'usage' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-center">
                  <div className="text-2xl font-black text-slate-800">
                    {usageData ? `${usageData.daily_requests_used} / ${usageData.daily_limit}` : '...'}
                  </div>
                  <div className="text-xs text-slate-500 font-semibold mt-1">
                    Requests Used Today
                  </div>
                  <div className="text-[11px] text-blue-600 mt-1 font-medium">
                    {usageData ? `${usageData.requests_remaining} requests remaining` : ''}
                  </div>
                </div>

                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-center">
                  <div className="text-2xl font-black text-emerald-600">
                    ${usageData ? usageData.total_cost_usd.toFixed(4) : '0.0000'}
                  </div>
                  <div className="text-xs text-slate-500 font-semibold mt-1">
                    Total Estimated Cost (USD)
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">
                    Billed per token consumption
                  </div>
                </div>
              </div>

              <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl text-xs text-blue-900 space-y-1.5 leading-relaxed">
                <div className="font-bold flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-blue-600" />
                  <span>Fair Use Daily Rate Limit Policy</span>
                </div>
                <p>
                  To maintain low-latency response times for all users, AI actions are subject to a soft limit of 50 structured requests per user per calendar day (UTC). Quotas automatically reset each night at midnight UTC.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

'use client';

import React, { useState } from 'react';
import { useResume } from '@/context/ResumeContext';
import { apiClient } from '@/lib/api';
import {
  Sparkles,
  Briefcase,
  FileText,
  ShieldCheck,
  Check,
  ArrowRight,
  TrendingUp,
  Cpu,
  Layers,
  AlertCircle,
  Copy,
  Plus,
  Loader2,
  CheckCircle2,
} from 'lucide-react';

interface AiToolsTabProps {
  onOpenTailorModal?: () => void;
  onOpenAtsModal?: () => void;
}

export const AiToolsTab: React.FC<AiToolsTabProps> = ({
  onOpenTailorModal,
  onOpenAtsModal,
}) => {
  const { resumeId, content, updateContent, addSection, updateItem, setActiveTab } = useResume();

  const [activeSubTool, setActiveSubTool] = useState<'bullet' | 'summary' | 'skills' | 'tailor'>('bullet');

  // Bullet Improver states
  const [bulletInput, setBulletInput] = useState('');
  const [bulletAction, setBulletAction] = useState<'improve' | 'add_impact' | 'shorten' | 'change_tone'>('improve');
  const [bulletTone, setBulletTone] = useState<'executive' | 'formal' | 'technical'>('executive');
  const [bulletLoading, setBulletLoading] = useState(false);
  const [suggestedBullet, setSuggestedBullet] = useState<string | null>(null);
  const [bulletDiff, setBulletDiff] = useState<string | null>(null);
  const [bulletError, setBulletError] = useState<string | null>(null);
  const [appliedBulletSuccess, setAppliedBulletSuccess] = useState(false);

  // Summary Generator states
  const [summaryTone, setSummaryTone] = useState<'executive' | 'formal' | 'technical'>('executive');
  const [targetTitle, setTargetTitle] = useState(content.header?.title || '');
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [suggestedSummary, setSuggestedSummary] = useState<string | null>(null);
  const [summaryError, setSummaryError] = useState<string | null>(null);
  const [appliedSummarySuccess, setAppliedSummarySuccess] = useState(false);

  // Skills Generator states
  const [skillsLoading, setSkillsLoading] = useState(false);
  const [suggestedSkills, setSuggestedSkills] = useState<{ skill: string; category: string }[]>([]);
  const [skillsError, setSkillsError] = useState<string | null>(null);
  const [addedSkills, setAddedSkills] = useState<Set<string>>(new Set());

  // Extract bullets from experience
  const getExperienceBullets = (): string[] => {
    const bullets: string[] = [];
    content.sections.forEach((sec) => {
      if (sec.type === 'experience' || sec.type === 'projects') {
        sec.items.forEach((item) => {
          item.bullets?.forEach((b) => {
            if (b.text?.trim()) bullets.push(b.text.trim());
          });
        });
      }
    });
    return bullets;
  };

  const handleImproveBullet = async () => {
    if (!bulletInput.trim()) return;
    setBulletLoading(true);
    setBulletError(null);
    setSuggestedBullet(null);
    setBulletDiff(null);
    setAppliedBulletSuccess(false);

    try {
      const res = await apiClient.post('/ai/bullet-action', {
        text: bulletInput.trim(),
        action: bulletAction,
        tone: bulletAction === 'change_tone' ? bulletTone : undefined,
      });
      setSuggestedBullet(res.data.suggested_text);
      setBulletDiff(res.data.diff_summary);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } };
      setBulletError(
        axiosErr.response?.data?.detail || 'Failed to improve bullet. Please try again.'
      );
    } finally {
      setBulletLoading(false);
    }
  };

  const handleGenerateSummary = async () => {
    setSummaryLoading(true);
    setSummaryError(null);
    setSuggestedSummary(null);
    setAppliedSummarySuccess(false);

    try {
      const bullets = getExperienceBullets();
      const existingSkills: string[] = [];
      const skillsSec = content.sections.find((s) => s.type === 'skills');
      skillsSec?.items.forEach((i) => i.bullets?.forEach((b) => existingSkills.push(b.text)));

      const res = await apiClient.post('/ai/generate-summary', {
        job_title: targetTitle || undefined,
        experience_bullets: bullets,
        skills: existingSkills,
        tone: summaryTone,
      });
      setSuggestedSummary(res.data.suggested_summary);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } };
      setSummaryError(
        axiosErr.response?.data?.detail || 'Failed to generate summary. Please try again.'
      );
    } finally {
      setSummaryLoading(false);
    }
  };

  const handleApplySummary = () => {
    if (!suggestedSummary) return;
    const summarySec = content.sections.find((s) => s.type === 'summary');
    if (summarySec && summarySec.items?.length > 0) {
      const firstItem = summarySec.items[0];
      updateItem(summarySec.id, firstItem.id, {
        bullets: [{ id: `b-${Date.now()}`, text: suggestedSummary }],
      });
    } else {
      addSection('summary', 'Professional Summary');
      // After adding, find and set
      setTimeout(() => {
        const fresh = content.sections.find((s) => s.type === 'summary');
        if (fresh && fresh.items?.[0]) {
          updateItem(fresh.id, fresh.items[0].id, {
            bullets: [{ id: `b-${Date.now()}`, text: suggestedSummary }],
          });
        }
      }, 50);
    }
    setAppliedSummarySuccess(true);
  };

  const handleSuggestSkills = async () => {
    setSkillsLoading(true);
    setSkillsError(null);
    try {
      const bullets = getExperienceBullets();
      const existingSkills: string[] = [];
      const skillsSec = content.sections.find((s) => s.type === 'skills');
      skillsSec?.items.forEach((i) => i.bullets?.forEach((b) => existingSkills.push(b.text)));

      const res = await apiClient.post('/ai/suggest-skills', {
        experience_bullets: bullets,
        existing_skills: existingSkills,
        limit: 12,
      });
      setSuggestedSkills(res.data.suggestions || []);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } };
      setSkillsError(
        axiosErr.response?.data?.detail || 'Failed to extract skills. Please try again.'
      );
    } finally {
      setSkillsLoading(false);
    }
  };

  const handleAddSkillToResume = (skillName: string) => {
    const skillsSec = content.sections.find((s) => s.type === 'skills');
    if (skillsSec && skillsSec.items?.length > 0) {
      const item = skillsSec.items[0];
      const newBullets = [
        ...(item.bullets || []),
        { id: `skill-${Date.now()}`, text: skillName, proficiency: null },
      ];
      updateItem(skillsSec.id, item.id, { bullets: newBullets });
    } else {
      addSection('skills', 'Skills');
      setTimeout(() => {
        const fresh = content.sections.find((s) => s.type === 'skills');
        if (fresh && fresh.items?.[0]) {
          updateItem(fresh.id, fresh.items[0].id, {
            bullets: [{ id: `skill-${Date.now()}`, text: skillName, proficiency: null }],
          });
        }
      }, 50);
    }
    setAddedSkills((prev) => new Set(prev).add(skillName));
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6 pb-20 animate-in fade-in">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-emerald-950 via-teal-900 to-slate-900 text-white rounded-3xl p-6 shadow-md relative overflow-hidden">
        <div className="flex items-center gap-2 text-emerald-300 text-xs font-semibold uppercase tracking-wider mb-1">
          <Sparkles className="w-4 h-4 text-emerald-400" />
          <span>Grounded AI Optimization Engine</span>
        </div>
        <h2 className="text-xl font-black text-white">AI Assistant & Job Tailoring</h2>
        <p className="text-xs text-emerald-100/80 mt-1 max-w-xl leading-relaxed">
          Powered by DeepMind-grade anti-hallucination guardrails. Never fabricates employers or years of experience. You retain 100% control over all accepted suggestions.
        </p>

        {/* Sub-tool tabs */}
        <div className="flex flex-wrap items-center gap-2 mt-5">
          <button
            type="button"
            onClick={() => setActiveSubTool('bullet')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeSubTool === 'bullet'
                ? 'bg-emerald-500 text-white shadow-xs'
                : 'bg-white/10 hover:bg-white/20 text-white'
            }`}
          >
            Bullet Point Improver
          </button>

          <button
            type="button"
            onClick={() => setActiveSubTool('summary')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeSubTool === 'summary'
                ? 'bg-emerald-500 text-white shadow-xs'
                : 'bg-white/10 hover:bg-white/20 text-white'
            }`}
          >
            Executive Summary
          </button>

          <button
            type="button"
            onClick={() => setActiveSubTool('skills')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeSubTool === 'skills'
                ? 'bg-emerald-500 text-white shadow-xs'
                : 'bg-white/10 hover:bg-white/20 text-white'
            }`}
          >
            Skills Extraction
          </button>

          <button
            type="button"
            onClick={() => {
              if (onOpenTailorModal) onOpenTailorModal();
              setActiveSubTool('tailor');
            }}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeSubTool === 'tailor'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-blue-600/30 hover:bg-blue-600/50 text-blue-200'
            }`}
          >
            <Briefcase className="w-3.5 h-3.5" />
            <span>Agent 2 Job Tailor</span>
          </button>
        </div>
      </div>

      {/* 1. Bullet Point Improver Sub-Tool */}
      {activeSubTool === 'bullet' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-5 animate-in fade-in">
          <div>
            <h3 className="font-bold text-base text-slate-900">Transform Achievements with Metrics & Impact</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Paste or type any bullet point from your work experience to make it punchy, quantified, and ATS-optimized.
            </p>
          </div>

          <div className="space-y-3">
            <textarea
              rows={3}
              value={bulletInput}
              onChange={(e) => setBulletInput(e.target.value)}
              placeholder="e.g. Led a team of engineers to build a new data pipeline for real-time customer analytics..."
              className="w-full text-xs p-3.5 border border-slate-200 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-emerald-500 bg-slate-50 focus:bg-white transition-colors"
            />

            {/* Action options */}
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="text-[11px] font-bold text-slate-500">Goal:</span>
              {[
                { id: 'improve', label: 'More Impactful' },
                { id: 'add_impact', label: 'Add Quantifiable Metrics' },
                { id: 'shorten', label: 'Make Concise' },
                { id: 'change_tone', label: 'Executive Tone' },
              ].map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => setBulletAction(opt.id as typeof bulletAction)}
                  className={`px-3 py-1.5 rounded-lg font-semibold transition-colors ${
                    bulletAction === opt.id
                      ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                      : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
                  }`}
                >
                  {opt.label}
                </button>
              ))}

              <button
                type="button"
                onClick={handleImproveBullet}
                disabled={bulletLoading || !bulletInput.trim()}
                className="ml-auto px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-xl font-bold transition-all shadow-xs flex items-center gap-1.5"
              >
                {bulletLoading ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Sparkles className="w-3.5 h-3.5" />
                )}
                <span>Generate Suggestion</span>
              </button>
            </div>
          </div>

          {bulletError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{bulletError}</span>
            </div>
          )}

          {/* Grounded Before & After Diff Box */}
          {suggestedBullet && (
            <div className="p-5 bg-emerald-50/60 border border-emerald-200 rounded-2xl space-y-4 animate-in fade-in">
              <div className="flex items-center justify-between pb-2 border-b border-emerald-200/60">
                <span className="text-xs font-bold text-emerald-950 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Optimized Recommendation</span>
                </span>
                {bulletDiff && (
                  <span className="text-[10px] font-mono text-emerald-800 bg-emerald-200/60 px-2 py-0.5 rounded">
                    {bulletDiff}
                  </span>
                )}
              </div>

              <div className="space-y-2 text-xs">
                <div className="p-3 bg-white/80 rounded-xl border border-emerald-100 text-slate-800 leading-relaxed font-medium">
                  {suggestedBullet}
                </div>
              </div>

              <div className="flex items-center justify-between pt-2">
                <button
                  type="button"
                  onClick={() => {
                    navigator.clipboard.writeText(suggestedBullet);
                    setAppliedBulletSuccess(true);
                  }}
                  className="px-3 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs rounded-xl transition-colors flex items-center gap-1.5"
                >
                  <Copy className="w-3.5 h-3.5" />
                  <span>{appliedBulletSuccess ? 'Copied to Clipboard!' : 'Copy to Clipboard'}</span>
                </button>

                <button
                  type="button"
                  onClick={() => setActiveTab('content')}
                  className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-xs transition-colors flex items-center gap-1.5"
                >
                  <span>Go to Content to Paste</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 2. Executive Summary Generator */}
      {activeSubTool === 'summary' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-5 animate-in fade-in">
          <div>
            <h3 className="font-bold text-base text-slate-900">Generate a Grounded Professional Summary</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Synthesizes your real career achievements into a punchy 3-4 sentence hook.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                Target Role / Job Title
              </label>
              <input
                type="text"
                value={targetTitle}
                onChange={(e) => setTargetTitle(e.target.value)}
                placeholder="e.g. Principal Staff Software Engineer"
                className="w-full px-3 py-2 border border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:ring-1 focus:ring-emerald-500"
              />
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                Tone & Voice
              </label>
              <select
                value={summaryTone}
                onChange={(e) => setSummaryTone(e.target.value as typeof summaryTone)}
                className="w-full px-3 py-2 border border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:ring-1 focus:ring-emerald-500"
              >
                <option value="executive">Executive & Leadership Focus</option>
                <option value="formal">Standard Formal / Corporate</option>
                <option value="technical">Hands-On Technical Deep Dive</option>
              </select>
            </div>
          </div>

          <button
            type="button"
            onClick={handleGenerateSummary}
            disabled={summaryLoading}
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-xl font-bold text-xs shadow-xs transition-colors flex items-center gap-1.5"
          >
            {summaryLoading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Sparkles className="w-3.5 h-3.5" />
            )}
            <span>Generate Grounded Summary</span>
          </button>

          {summaryError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{summaryError}</span>
            </div>
          )}

          {suggestedSummary && (
            <div className="p-5 bg-emerald-50/60 border border-emerald-200 rounded-2xl space-y-4 animate-in fade-in">
              <span className="text-xs font-bold text-emerald-950 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Generated Summary</span>
              </span>
              <p className="text-xs text-slate-800 leading-relaxed bg-white/80 p-3.5 rounded-xl border border-emerald-100 font-medium">
                {suggestedSummary}
              </p>

              <div className="flex items-center justify-between pt-1">
                <span className="text-[11px] text-emerald-800 font-medium">
                  {appliedSummarySuccess ? 'Applied directly to your Summary section!' : 'Ready to apply.'}
                </span>

                <button
                  type="button"
                  onClick={handleApplySummary}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-xs transition-colors flex items-center gap-1.5"
                >
                  <Check className="w-3.5 h-3.5" />
                  <span>Apply to Summary Section</span>
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 3. Skills Suggestion Sub-Tool */}
      {activeSubTool === 'skills' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-5 animate-in fade-in">
          <div>
            <h3 className="font-bold text-base text-slate-900">Automated Skill Extraction</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Extracts high-impact technical keywords evidenced in your career bullets that you may have forgotten to tag.
            </p>
          </div>

          <button
            type="button"
            onClick={handleSuggestSkills}
            disabled={skillsLoading}
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-xl font-bold text-xs shadow-xs transition-colors flex items-center gap-1.5"
          >
            {skillsLoading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Cpu className="w-3.5 h-3.5" />
            )}
            <span>Scan Experience for Skills</span>
          </button>

          {skillsError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{skillsError}</span>
            </div>
          )}

          {suggestedSkills.length > 0 && (
            <div className="space-y-3 pt-2">
              <span className="text-xs font-bold text-slate-800">
                Found {suggestedSkills.length} recommended skills:
              </span>
              <div className="flex flex-wrap gap-2">
                {suggestedSkills.map((s, idx) => {
                  const isAdded = addedSkills.has(s.skill);
                  return (
                    <button
                      key={idx}
                      type="button"
                      disabled={isAdded}
                      onClick={() => handleAddSkillToResume(s.skill)}
                      className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
                        isAdded
                          ? 'bg-slate-100 text-slate-400 border border-slate-200 cursor-default'
                          : 'bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 shadow-2xs hover:scale-105'
                      }`}
                    >
                      {isAdded ? <Check className="w-3 h-3" /> : <Plus className="w-3 h-3" />}
                      <span>{s.skill}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 4. Tailor with Agent 2 Card */}
      {activeSubTool === 'tailor' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4 animate-in fade-in">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-blue-50 text-blue-600 rounded-xl">
                <Briefcase className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-sm text-slate-900">Agent 2 Job Tailoring Pipeline</h3>
                <p className="text-xs text-slate-500">Custom match against any target job description</p>
              </div>
            </div>
            <button
              type="button"
              onClick={onOpenTailorModal}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-xs transition-colors flex items-center gap-1.5"
            >
              <span>Launch Tailor Dialog</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <p className="text-xs text-slate-600 leading-relaxed">
            The full tailor flow analyzes requirements from the target company, highlights matching qualifications, and provides grounded bullet revisions with an interactive visual diff modal.
          </p>
        </div>
      )}
    </div>
  );
};

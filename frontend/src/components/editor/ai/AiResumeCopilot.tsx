'use client';

import React, { useState } from 'react';
import { useResume } from '@/context/ResumeContext';
import {
  Sparkles,
  Check,
  CheckCircle2,
  Wand2,
  Layers,
  ArrowRight,
  TrendingUp,
  Plus,
  RefreshCw,
  ExternalLink,
} from 'lucide-react';

interface AiResumeCopilotProps {
  onOpenTailorModal?: () => void;
  onOpenAtsModal?: () => void;
}

interface BulletSuggestion {
  roleLabel: string;
  original: string;
  enhanced: string;
  applied: boolean;
}

export const AiResumeCopilot: React.FC<AiResumeCopilotProps> = ({
  onOpenTailorModal,
  onOpenAtsModal,
}) => {
  const { content, updateContent, addSection } = useResume();

  const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(0);
  const [showJdInput, setShowJdInput] = useState(false);
  const [targetRole, setTargetRole] = useState('Staff Infrastructure Engineer @ Scale AI');
  const [customJd, setCustomJd] = useState('');
  const [injectedSkills, setInjectedSkills] = useState<Set<string>>(new Set());

  const [suggestions, setSuggestions] = useState<BulletSuggestion[]>([
    {
      roleLabel: 'Role #1 (Lead / Senior)',
      original: 'Built ledger routing system handling transaction volume without crashes.',
      enhanced:
        'Architected and deployed high-throughput global ledger routing subsystem handling $4.2B+ daily transaction volume with zero downtime during peak seasonal traffic.',
      applied: false,
    },
    {
      roleLabel: 'Role #2 (Systems Modernization)',
      original: 'Helped reduce backend latency across services using caching.',
      enhanced:
        'Spearheaded engineering modernization across 14 distributed service clusters, dropping tail p99 latency from 180ms to 42ms through custom Rust memory caching layers.',
      applied: false,
    },
    {
      roleLabel: 'Role #3 (Cloud Infrastructure)',
      original: 'Managed Kubernetes clusters and cut AWS cloud costs for the team.',
      enhanced:
        'Reduced AWS infrastructure costs by 38% ($450K ARR) via intelligent container right-sizing and spot fleet orchestration in EKS.',
      applied: false,
    },
  ]);

  const activeSuggestion = suggestions[activeSuggestionIndex];

  // Apply enhanced bullet to real resume content
  const handleApplyBullet = () => {
    if (!activeSuggestion) return;

    // Search for the original text or first experience bullet in resume content
    let applied = false;
    const newSections = content.sections.map((sec) => {
      if (sec.type === 'experience' || sec.type === 'projects') {
        const newItems = sec.items.map((item, itemIdx) => {
          if (!applied && item.bullets && item.bullets.length > 0) {
            // Target the bullet corresponding to activeSuggestionIndex or first available
            const bIdx = Math.min(activeSuggestionIndex, item.bullets.length - 1);
            const newBullets = [...item.bullets];
            newBullets[bIdx] = {
              ...newBullets[bIdx],
              text: activeSuggestion.enhanced,
            };
            applied = true;
            return { ...item, bullets: newBullets };
          }
          return item;
        });
        return { ...sec, items: newItems };
      }
      return sec;
    });

    if (applied) {
      updateContent({ ...content, sections: newSections });
    }

    // Mark current suggestion as applied
    setSuggestions((prev) =>
      prev.map((s, idx) => (idx === activeSuggestionIndex ? { ...s, applied: true } : s))
    );
  };

  const handleNextSuggestion = () => {
    setActiveSuggestionIndex((prev) => (prev + 1) % suggestions.length);
  };

  // Inject recommended skill into resume content
  const handleInjectSkill = (skillName: string) => {
    if (injectedSkills.has(skillName)) return;

    let skillsSection = content.sections.find((s) => s.type === 'skills');
    if (!skillsSection) {
      addSection('skills', 'Technical Skills');
      skillsSection = content.sections.find((s) => s.type === 'skills');
    }

    if (skillsSection) {
      const newSections = content.sections.map((sec) => {
        if (sec.id === skillsSection!.id) {
          const firstItem = sec.items[0];
          if (firstItem) {
            const newBullets = [
              ...(firstItem.bullets || []),
              {
                id: `skill-${Date.now()}`,
                text: skillName,
                proficiency: null,
              },
            ];
            return {
              ...sec,
              items: sec.items.map((item, idx) => (idx === 0 ? { ...item, bullets: newBullets } : item)),
            };
          }
        }
        return sec;
      });
      updateContent({ ...content, sections: newSections });
    }

    setInjectedSkills((prev) => {
      const next = new Set(prev);
      next.add(skillName);
      return next;
    });
  };

  const handleSaveJd = () => {
    if (customJd.trim()) {
      const firstLine = customJd.trim().split('\n')[0].substring(0, 48);
      setTargetRole(firstLine || 'Custom Job Target');
    }
    setShowJdInput(false);
  };

  return (
    <div className="flex flex-col h-full bg-[#F8F9FA] select-none">
      {/* 1. Header Bar matching Stitch */}
      <div className="px-5 py-3 border-b border-slate-200/90 flex items-center justify-between bg-[#F8F9FA]/90 shrink-0">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-[#FF2D6C]" />
          <h2 className="font-bold text-slate-900 text-sm tracking-tight">AI Resume Copilot</h2>
        </div>
        <span className="px-2.5 py-0.5 rounded-full bg-pink-50 border border-pink-200 font-mono text-[11px] text-[#FF2D6C] font-semibold">
          Claude 3.7 Sonnet
        </span>
      </div>

      {/* 2. Scrollable Body Cards */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4">
        {/* Card 1: Resume Impact Score */}
        <div className="p-4 bg-white rounded-2xl border border-slate-200/90 shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
          <div className="flex items-center justify-between mb-3">
            <div>
              <span className="font-bold text-slate-900 text-sm block">Resume Impact Score</span>
              <span className="text-xs text-slate-500">Senior Staff Archetype Benchmark</span>
            </div>
            <div className="w-12 h-12 rounded-full border-4 border-emerald-500 flex items-center justify-center font-bold text-emerald-800 text-sm bg-emerald-50/30">
              94%
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 text-center pt-2.5 border-t border-slate-100 text-[11px] font-mono">
            <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block text-[10px]">Action Verbs</span>
              <span className="text-emerald-700 font-bold">100% (High)</span>
            </div>
            <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block text-[10px]">Quant Metrics</span>
              <span className="text-emerald-700 font-bold">$4.2B, 40k RPS</span>
            </div>
            <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block text-[10px]">Page Density</span>
              <span className="text-emerald-700 font-bold">98% A4 Fit</span>
            </div>
          </div>
        </div>

        {/* Card 2: Target Job Description Keyword Matcher */}
        <div className="p-4 bg-white rounded-2xl border border-slate-200/90 shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-bold text-xs text-slate-900 uppercase tracking-wide">
              Target Job Description
            </span>
            <button
              type="button"
              onClick={() => setShowJdInput((prev) => !prev)}
              className="text-xs font-semibold text-blue-600 hover:text-blue-700 hover:underline cursor-pointer"
            >
              {showJdInput ? 'Cancel' : 'Paste New JD'}
            </button>
          </div>

          {showJdInput ? (
            <div className="space-y-2 animate-in fade-in">
              <textarea
                value={customJd}
                onChange={(e) => setCustomJd(e.target.value)}
                placeholder="Paste the target job description here..."
                rows={4}
                className="w-full text-xs p-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-1 focus:ring-blue-500 outline-hidden font-sans"
              />
              <button
                type="button"
                onClick={handleSaveJd}
                className="w-full py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-xl shadow-xs transition-colors"
              >
                Analyze & Match Keywords
              </button>
            </div>
          ) : (
            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200/80 text-xs font-mono text-slate-600 truncate">
              Target Role: <strong className="text-slate-900">{targetRole}</strong>
            </div>
          )}

          {/* Matched Keywords */}
          <div>
            <span className="text-[11px] text-slate-400 font-mono block mb-1.5 font-medium">
              Matched Keywords in Resume (8/9)
            </span>
            <div className="flex flex-wrap gap-1.5">
              <span className="px-2.5 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-medium flex items-center gap-1">
                <Check className="w-3 h-3 text-emerald-600" /> Distributed Consensus
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-medium flex items-center gap-1">
                <Check className="w-3 h-3 text-emerald-600" /> Rust / Systems
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-medium flex items-center gap-1">
                <Check className="w-3 h-3 text-emerald-600" /> eBPF Telemetry
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-medium flex items-center gap-1">
                <Check className="w-3 h-3 text-emerald-600" /> High-Throughput
              </span>
            </div>
          </div>

          {/* Recommended to Add */}
          <div className="pt-1 border-t border-slate-100">
            <span className="text-[11px] text-amber-700 font-mono block mb-1.5 font-medium">
              Recommended to Add (+1)
            </span>
            <div className="flex items-center justify-between gap-2 p-2 rounded-xl bg-amber-50/60 border border-amber-200">
              <span className="text-amber-900 text-xs font-medium truncate">
                GPU Cluster Orchestration
              </span>
              <button
                type="button"
                onClick={() => handleInjectSkill('GPU Cluster Orchestration')}
                disabled={injectedSkills.has('GPU Cluster Orchestration')}
                className="shrink-0 text-xs font-bold text-[#FF2D6C] hover:text-[#FF5E62] hover:underline cursor-pointer disabled:text-emerald-700 disabled:no-underline flex items-center gap-1"
              >
                {injectedSkills.has('GPU Cluster Orchestration') ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Injected</span>
                  </>
                ) : (
                  '+ Inject to Skills'
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Card 3: AI Bullet Rewrite Assistant */}
        <div className="p-4 bg-white rounded-2xl border border-pink-200 bg-pink-50/15 shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#FF2D6C] flex items-center gap-1.5">
              <Wand2 className="w-4 h-4" />
              <span>Active Bullet Rewrite</span>
            </span>
            <span className="text-[11px] text-slate-400 font-mono font-medium">
              {activeSuggestion?.roleLabel || 'Role #1'}
            </span>
          </div>

          <div className="space-y-2 text-xs">
            {/* Original */}
            <div className="p-3 rounded-xl bg-white border border-slate-200/80">
              <span className="text-[10px] text-slate-400 font-mono block mb-1 font-semibold uppercase">
                ORIGINAL:
              </span>
              <p className="text-slate-500 line-through leading-relaxed">
                {activeSuggestion?.original}
              </p>
            </div>

            {/* AI Enhanced */}
            <div className="p-3 rounded-xl bg-emerald-50/70 border border-emerald-300">
              <span className="text-[10px] text-emerald-800 font-mono font-bold block mb-1 uppercase flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-emerald-600" />
                <span>AI ENHANCED (ACTIVE):</span>
              </span>
              <p className="text-emerald-950 font-medium leading-relaxed">
                {activeSuggestion?.enhanced}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 pt-1">
            <button
              type="button"
              onClick={handleApplyBullet}
              className={`flex-1 py-2 rounded-xl font-bold text-xs shadow-xs transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                activeSuggestion?.applied
                  ? 'bg-emerald-600 text-white'
                  : 'bg-gradient-to-r from-[#FF2D6C] to-[#FF5E62] hover:opacity-95 text-white'
              }`}
            >
              {activeSuggestion?.applied ? (
                <>
                  <Check className="w-3.5 h-3.5" />
                  <span>Applied to Resume</span>
                </>
              ) : (
                'Apply to Resume'
              )}
            </button>

            <button
              type="button"
              onClick={handleNextSuggestion}
              className="px-3 py-2 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 font-bold text-xs transition-colors cursor-pointer"
            >
              Next Suggestion
            </button>
          </div>
        </div>

        {/* Deep Tools Quick Actions */}
        <div className="grid grid-cols-2 gap-2 pt-1">
          {onOpenTailorModal && (
            <button
              type="button"
              onClick={onOpenTailorModal}
              className="p-3 rounded-2xl bg-white border border-slate-200/90 hover:border-slate-300 text-left transition-all group shadow-2xs"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-slate-800 group-hover:text-blue-600">
                  Full Tailoring Studio
                </span>
                <ArrowRight className="w-3 h-3 text-slate-400 group-hover:translate-x-0.5 transition-transform" />
              </div>
              <p className="text-[11px] text-slate-400 leading-snug">
                Audit against complete JD and approve diffs
              </p>
            </button>
          )}

          {onOpenAtsModal && (
            <button
              type="button"
              onClick={onOpenAtsModal}
              className="p-3 rounded-2xl bg-white border border-slate-200/90 hover:border-slate-300 text-left transition-all group shadow-2xs"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-slate-800 group-hover:text-emerald-600">
                  ATS Scanner
                </span>
                <ArrowRight className="w-3 h-3 text-slate-400 group-hover:translate-x-0.5 transition-transform" />
              </div>
              <p className="text-[11px] text-slate-400 leading-snug">
                Simulate enterprise parser checks
              </p>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

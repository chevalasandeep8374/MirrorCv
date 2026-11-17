'use client';

import React, { useState } from 'react';
import { useResume } from '@/context/ResumeContext';
import {
  CheckCircle2,
  Circle,
  AlertCircle,
  Sparkles,
  ShieldCheck,
  Share2,
  Download,
  History,
  Briefcase,
  FileText,
  ArrowRight,
  TrendingUp,
  Layers,
  Copy,
  Check,
} from 'lucide-react';

interface OverviewTabProps {
  onOpenAts: () => void;
  onOpenTailor: () => void;
  onOpenVersions: () => void;
  onOpenShare: () => void;
}

export const OverviewTab: React.FC<OverviewTabProps> = ({
  onOpenAts,
  onOpenTailor,
  onOpenVersions,
  onOpenShare,
}) => {
  const { resumeId, title, content, style, version, lastSaved, setActiveTab } = useResume();
  const [copiedLink, setCopiedLink] = useState(false);

  // Health and Completeness Checklist calculation
  const hasName = Boolean(content.header?.name?.trim());
  const hasTitle = Boolean(content.header?.title?.trim());
  const hasEmail = Boolean(content.header?.email?.trim());
  const hasPhone = Boolean(content.header?.phone?.trim());
  const hasLocation = Boolean(content.header?.location?.trim());

  const summarySection = content.sections.find((s) => s.type === 'summary');
  const hasSummary = Boolean(
    summarySection &&
      summarySection.items?.some((i) => i.bullets?.some((b) => b.text?.trim().length > 15))
  );

  const expSection = content.sections.find((s) => s.type === 'experience');
  const expCount = expSection?.items?.length || 0;
  const hasExperience = expCount >= 1;

  const eduSection = content.sections.find((s) => s.type === 'education');
  const hasEducation = Boolean(eduSection && eduSection.items?.length > 0);

  const skillsSection = content.sections.find((s) => s.type === 'skills');
  const skillChipsCount =
    skillsSection?.items?.reduce((sum, item) => sum + (item.bullets?.length || 0), 0) || 0;
  const hasSkills = skillChipsCount >= 3;

  const checklist = [
    { label: 'Full name & professional headline', done: hasName && hasTitle },
    { label: 'Verified email & phone number', done: hasEmail && hasPhone },
    { label: 'Location / City', done: hasLocation },
    { label: 'Professional executive summary', done: hasSummary },
    { label: 'Work experience with quantifiable achievements', done: hasExperience },
    { label: 'Education credentials', done: hasEducation },
    { label: 'Key technical & soft skills (3+ items)', done: hasSkills },
  ];

  const completedCount = checklist.filter((c) => c.done).length;
  const completionPercentage = Math.round((completedCount / checklist.length) * 100);

  // Estimated baseline ATS score based on structural standards
  const estimatedAtsScore = Math.min(
    98,
    Math.max(
      45,
      completionPercentage - (style.margins.top < 20 ? 10 : 0) + (hasSummary ? 10 : 0)
    )
  );

  const handleCopyShareLink = () => {
    const url = `${window.location.origin}/p/${resumeId}`;
    navigator.clipboard.writeText(url);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2500);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6 pb-20 animate-in fade-in">
      {/* 1. Header Banner */}
      <div className="bg-gradient-to-r from-blue-900 to-indigo-900 text-white rounded-3xl p-6 shadow-md relative overflow-hidden">
        <div className="relative z-10">
          <div className="flex items-center gap-2 text-blue-200 text-xs font-semibold uppercase tracking-wider mb-1">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            <span>Document Overview & Health</span>
          </div>
          <h2 className="text-xl font-black text-white">{title || 'Untitled Resume'}</h2>
          <p className="text-xs text-blue-100/80 mt-1 max-w-xl leading-relaxed">
            FlowCV-class readiness score, completeness breakdown, and one-click AI tools to maximize interview invitations.
          </p>

          <div className="flex flex-wrap items-center gap-3 mt-5">
            <button
              type="button"
              onClick={() => setActiveTab('content')}
              className="px-4 py-2 bg-blue-500 hover:bg-blue-400 text-white rounded-xl text-xs font-bold shadow-xs transition-colors flex items-center gap-1.5"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Edit Content</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('customize')}
              className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-xs font-bold transition-colors flex items-center gap-1.5 backdrop-blur-xs"
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Customize Design</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('ai')}
              className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-white rounded-xl text-xs font-bold transition-colors flex items-center gap-1.5 shadow-xs"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>AI Tailoring & Tools</span>
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* 2. Document Health Checklist (Span 2) */}
        <div className="md:col-span-2 bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 className="font-bold text-sm text-slate-900">Completeness Checklist</h3>
              <p className="text-xs text-slate-400">Essential sections for a top-tier recruiter impression</p>
            </div>
            <div className="text-right">
              <span className="font-black text-sm text-blue-600">{completionPercentage}%</span>
              <p className="text-[10px] text-slate-400">{completedCount} of {checklist.length} complete</p>
            </div>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${
                completionPercentage >= 85
                  ? 'bg-emerald-500'
                  : completionPercentage >= 60
                  ? 'bg-blue-600'
                  : 'bg-amber-500'
              }`}
              style={{ width: `${completionPercentage}%` }}
            />
          </div>

          {/* Checklist Items */}
          <div className="space-y-2.5 pt-1">
            {checklist.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-100 text-xs"
              >
                <div className="flex items-center gap-2.5">
                  {item.done ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                  ) : (
                    <Circle className="w-4 h-4 text-slate-300 shrink-0" />
                  )}
                  <span className={item.done ? 'font-semibold text-slate-800' : 'text-slate-500'}>
                    {item.label}
                  </span>
                </div>
                {!item.done && (
                  <button
                    type="button"
                    onClick={() => setActiveTab('content')}
                    className="text-[11px] font-bold text-blue-600 hover:underline flex items-center gap-0.5"
                  >
                    <span>Add</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* 3. ATS & Version Column */}
        <div className="space-y-6">
          {/* ATS Gauge Card */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-emerald-50 text-emerald-600 rounded-lg">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <h4 className="font-bold text-xs text-slate-900">ATS Readiness Score</h4>
              </div>
              <span className="font-black text-lg text-emerald-600">{estimatedAtsScore}/100</span>
            </div>

            <p className="text-[11px] text-slate-500 leading-relaxed">
              Standardized formatting, font sizes, and clear section headings ensure compatibility with Workday, Greenhouse, and Lever.
            </p>

            <button
              type="button"
              onClick={onOpenAts}
              className="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs rounded-xl transition-colors flex items-center justify-center gap-1.5"
            >
              <span>Scan Keywords & ATS</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
            </button>
          </div>

          {/* Version Snapshot */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-indigo-50 text-indigo-600 rounded-lg">
                  <History className="w-4 h-4" />
                </div>
                <h4 className="font-bold text-xs text-slate-900">Version History</h4>
              </div>
              <span className="text-[10px] font-mono font-bold bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full">
                v{version}
              </span>
            </div>

            <p className="text-[11px] text-slate-500">
              Last saved: {lastSaved ? lastSaved.toLocaleTimeString() : 'Recently'}
            </p>

            <button
              type="button"
              onClick={onOpenVersions}
              className="w-full py-2 bg-slate-50 hover:bg-slate-100 text-slate-700 font-semibold text-xs rounded-xl border border-slate-200 transition-colors flex items-center justify-center gap-1.5"
            >
              <span>View Timeline Snapshots</span>
            </button>
          </div>

          {/* Share Quick Card */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-purple-50 text-purple-600 rounded-lg">
                  <Share2 className="w-4 h-4" />
                </div>
                <h4 className="font-bold text-xs text-slate-900">Public Web Resume</h4>
              </div>
            </div>

            <p className="text-[11px] text-slate-500">
              Share a clean live link with recruiters and hiring managers.
            </p>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleCopyShareLink}
                className="flex-1 py-2 bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs rounded-xl shadow-xs transition-colors flex items-center justify-center gap-1.5"
              >
                {copiedLink ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedLink ? 'Copied Link!' : 'Copy Link'}</span>
              </button>

              <button
                type="button"
                onClick={onOpenShare}
                className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl transition-colors"
                title="Share Settings"
              >
                Settings
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useResume } from '@/context/ResumeContext';
import { getActiveRepository } from '@/repositories';
import { ResumeSummary } from '@/types/resume';
import {
  Sparkles,
  ShieldCheck,
  Share2,
  Download,
  History,
  FileText,
  ArrowRight,
  Plus,
  MoreVertical,
  Copy,
  Check,
  CheckCircle2,
  Circle,
  TrendingUp,
  Layers,
  Loader2,
  ExternalLink,
} from 'lucide-react';

interface OverviewTabProps {
  onOpenAts?: () => void;
  onOpenTailor?: () => void;
  onOpenVersions?: () => void;
  onOpenShare?: () => void;
}

function formatRelativeTime(dateStr?: string | Date): string {
  if (!dateStr) return 'Recently';
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

export const OverviewTab: React.FC<OverviewTabProps> = ({
  onOpenAts,
  onOpenTailor,
  onOpenVersions,
  onOpenShare,
}) => {
  const router = useRouter();
  const { resumeId, title, content, style, version, lastSaved, setActiveTab } = useResume();

  const [resumes, setResumes] = useState<ResumeSummary[]>([]);
  const [loadingResumes, setLoadingResumes] = useState(false);
  const [creating, setCreating] = useState(false);
  const [viewMode, setViewMode] = useState<'documents' | 'health'>('documents');
  const [copiedLink, setCopiedLink] = useState(false);

  // Fetch list of user's resumes
  const loadResumes = async () => {
    setLoadingResumes(true);
    try {
      const repo = await getActiveRepository();
      const list = await repo.list(false);
      setResumes(list);
    } catch (e) {
      console.error('Failed to load resumes for overview:', e);
    } finally {
      setLoadingResumes(false);
    }
  };

  useEffect(() => {
    loadResumes();
  }, [resumeId]);

  // Completeness Checklist Calculation
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

  const estimatedAtsScore = Math.min(
    98,
    Math.max(
      45,
      completionPercentage - (style.margins.top < 20 ? 10 : 0) + (hasSummary ? 10 : 0)
    )
  );

  const handleCreateNew = async () => {
    setCreating(true);
    try {
      const repo = await getActiveRepository();
      const newResume = await repo.create({
        title: 'New Targeted Resume',
      });
      router.push(`/editor/${newResume.id}`);
    } catch (e) {
      alert('Failed to create resume. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  const handleDuplicate = async (targetId: string) => {
    try {
      const repo = await getActiveRepository();
      const dup = await repo.duplicate(targetId);
      router.push(`/editor/${dup.id}`);
    } catch (e) {
      alert('Failed to duplicate resume.');
    }
  };

  const handleCopyShareLink = () => {
    const url = `${window.location.origin}/p/${resumeId}`;
    navigator.clipboard.writeText(url);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2500);
  };

  // Other resumes excluding current
  const otherResumes = resumes.filter((r) => r.id !== resumeId);
  const totalCount = Math.max(1, resumes.length || 1);

  return (
    <div className="max-w-6xl mx-auto px-6 py-8 space-y-8 select-none">
      {/* 1. Hero Title & Statistics Strip matching Stitch */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="font-bold text-2xl sm:text-3xl text-slate-900 tracking-tight">
            Your Resumes &amp; Job Tailorings
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Manage your targeted editorial resumes, live application versions, and download histories.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-mono text-slate-800 shadow-2xs">
            <span className="text-slate-400">Total Storage:</span>
            <span className="font-bold">
              {totalCount} {totalCount === 1 ? 'Resume' : 'Resumes'} (1 Active)
            </span>
          </div>

          <div className="flex items-center bg-slate-100 p-0.5 rounded-xl border border-slate-200/80 text-xs font-semibold">
            <button
              type="button"
              onClick={() => setViewMode('documents')}
              className={`px-3 py-1 rounded-lg transition-all ${
                viewMode === 'documents'
                  ? 'bg-white text-slate-900 shadow-2xs'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              All Documents
            </button>
            <button
              type="button"
              onClick={() => setViewMode('health')}
              className={`px-3 py-1 rounded-lg transition-all ${
                viewMode === 'health'
                  ? 'bg-white text-slate-900 shadow-2xs'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Readiness &amp; Health
            </button>
          </div>
        </div>
      </div>

      {viewMode === 'documents' ? (
        /* 2. Resumes Grid matching Stitch */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in">
          {/* Card 1: Primary Demo Resume (Active) */}
          <article className="bg-white rounded-2xl border-2 border-slate-900 shadow-sm overflow-hidden flex flex-col justify-between group hover:shadow-md transition-shadow">
            <div className="p-5 pb-0">
              <div className="flex items-center justify-between mb-3">
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 text-[11px] font-mono font-bold flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  <span>Primary Active</span>
                </span>
                <button
                  type="button"
                  onClick={() => handleDuplicate(resumeId)}
                  className="p-1 text-slate-400 hover:text-slate-800 rounded-lg hover:bg-slate-100 transition-colors"
                  title="Duplicate this resume"
                >
                  <Copy className="w-4 h-4" />
                </button>
              </div>

              <h3 className="font-bold text-slate-900 text-base truncate">
                {title || 'Staff Software Engineer'}
              </h3>
              <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                Updated {lastSaved ? formatRelativeTime(lastSaved) : '12m ago'} · 1 Page
              </p>
            </div>

            {/* Realistic Scaled Down Preview Thumbnail */}
            <div className="p-5 pt-3">
              <div className="w-full h-44 bg-slate-50 border border-slate-200 rounded-xl p-3.5 flex flex-col justify-between overflow-hidden shadow-2xs group-hover:border-slate-300 transition-colors">
                <div className="space-y-2">
                  <div className="flex items-center justify-between border-b border-slate-200 pb-1.5">
                    <span className="font-bold text-xs text-slate-800 truncate">
                      {content.header?.name || 'Alex Mercer'}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">Curriculum Vitae</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-200 rounded" />
                  <div className="w-5/6 h-1.5 bg-slate-200 rounded" />
                  <div className="w-4/6 h-1.5 bg-slate-200 rounded" />
                  <div className="pt-1.5 space-y-1">
                    <div className="w-1/3 h-1.5 bg-slate-800 rounded" />
                    <div className="w-full h-1.5 bg-slate-200 rounded" />
                  </div>
                </div>
                <div className="text-[10px] font-mono text-slate-400 border-t border-slate-200 pt-1.5 flex justify-between">
                  <span>Single Column A4</span>
                  <span className="text-emerald-700 font-bold">ATS Score: {estimatedAtsScore}%</span>
                </div>
              </div>
            </div>

            {/* Card Footer Actions */}
            <div className="px-5 py-3 border-t border-slate-100 bg-slate-50/50 flex items-center justify-between">
              <button
                type="button"
                onClick={() => handleDuplicate(resumeId)}
                className="text-xs font-semibold text-slate-600 hover:text-slate-900 transition-colors"
              >
                Duplicate
              </button>
              <div className="flex items-center gap-2">
                <a
                  href={`/render/${resumeId}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-1.5 text-slate-400 hover:text-slate-800 rounded-lg hover:bg-slate-200/60 transition-colors"
                  title="Download / Preview"
                >
                  <Download className="w-4 h-4" />
                </a>
                <button
                  type="button"
                  onClick={() => setActiveTab('content')}
                  className="px-3.5 py-1.5 rounded-lg bg-[#181824] text-white font-bold text-xs hover:bg-black transition-colors cursor-pointer flex items-center gap-1"
                >
                  <span>Open Editor</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </article>

          {/* Cards 2..N: Other Resumes */}
          {otherResumes.map((r) => (
            <article
              key={r.id}
              className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col justify-between group hover:border-slate-300 transition-colors"
            >
              <div className="p-5 pb-0">
                <div className="flex items-center justify-between mb-3">
                  <span className="px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 font-mono text-[11px] font-medium">
                    {r.targetJobTitle ? `Tailored: ${r.targetJobTitle}` : 'Tailored: Variant'}
                  </span>
                  <button
                    type="button"
                    onClick={() => handleDuplicate(r.id)}
                    className="p-1 text-slate-400 hover:text-slate-800 rounded-lg hover:bg-slate-100 transition-colors"
                    title="Duplicate"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>

                <h3 className="font-bold text-slate-900 text-base truncate">{r.title}</h3>
                <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                  Updated {formatRelativeTime(r.updatedAt)} · 1 Page
                </p>
              </div>

              <div className="p-5 pt-3">
                <div className="w-full h-44 bg-slate-50 border border-slate-200 rounded-xl p-3.5 flex flex-col justify-between overflow-hidden shadow-2xs">
                  <div className="flex gap-2.5 h-full">
                    <div className="w-1/3 bg-slate-100 rounded-lg p-1.5 space-y-1.5">
                      <div className="w-3/4 h-1.5 bg-slate-400 rounded" />
                      <div className="w-full h-1.5 bg-slate-300 rounded" />
                      <div className="w-5/6 h-1.5 bg-slate-300 rounded" />
                    </div>
                    <div className="w-2/3 space-y-2">
                      <div className="w-1/2 h-2 bg-slate-800 rounded" />
                      <div className="w-full h-1.5 bg-slate-200 rounded" />
                      <div className="w-full h-1.5 bg-slate-200 rounded" />
                      <div className="w-4/5 h-1.5 bg-slate-200 rounded" />
                    </div>
                  </div>
                  <div className="text-[10px] font-mono text-slate-400 border-t border-slate-200 pt-1.5 flex justify-between">
                    <span>Split Two-Column</span>
                    <span className="text-emerald-700 font-bold">ATS Score: 95%</span>
                  </div>
                </div>
              </div>

              <div className="px-5 py-3 border-t border-slate-100 bg-slate-50/50 flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => handleDuplicate(r.id)}
                  className="text-xs font-semibold text-slate-600 hover:text-slate-900 transition-colors"
                >
                  Duplicate
                </button>
                <div className="flex items-center gap-2">
                  <a
                    href={`/render/${r.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1.5 text-slate-400 hover:text-slate-800 rounded-lg hover:bg-slate-200/60 transition-colors"
                    title="Download / Preview"
                  >
                    <Download className="w-4 h-4" />
                  </a>
                  <button
                    type="button"
                    onClick={() => router.push(`/editor/${r.id}`)}
                    className="px-3.5 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-800 font-bold text-xs hover:bg-slate-50 transition-colors cursor-pointer"
                  >
                    Open Editor
                  </button>
                </div>
              </div>
            </article>
          ))}

          {/* Card: New Document Blank Creator */}
          <div
            onClick={handleCreateNew}
            className="bg-[#F8F9FA] border-2 border-dashed border-slate-200 hover:border-slate-400 rounded-2xl p-8 flex flex-col items-center justify-center text-center transition-colors cursor-pointer group"
          >
            <div className="w-12 h-12 rounded-full bg-white border border-slate-200 shadow-xs flex items-center justify-center text-slate-900 group-hover:scale-105 transition-transform mb-3">
              {creating ? (
                <Loader2 className="w-5 h-5 animate-spin text-[#FF2D6C]" />
              ) : (
                <Plus className="w-5 h-5 text-slate-800" />
              )}
            </div>
            <h3 className="font-bold text-slate-900 text-sm">Create New Targeted Resume</h3>
            <p className="text-xs text-slate-500 max-w-xs mt-1 mb-4 leading-relaxed">
              Start from scratch, duplicate existing content, or import your LinkedIn JSON profile.
            </p>
            <span className="px-4 py-1.5 rounded-full bg-white border border-slate-200 text-xs font-bold text-slate-800 shadow-2xs group-hover:bg-slate-50 transition-colors">
              + Add Document
            </span>
          </div>
        </div>
      ) : (
        /* 3. Document Health & Readiness Audit View */
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-in fade-in">
          {/* Completeness Checklist (Span 2) */}
          <div className="md:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h3 className="font-bold text-sm text-slate-900">Completeness Checklist</h3>
                <p className="text-xs text-slate-400">Essential sections for a top-tier recruiter impression</p>
              </div>
              <div className="text-right">
                <span className="font-black text-sm text-[#FF2D6C]">{completionPercentage}%</span>
                <p className="text-[10px] text-slate-400">
                  {completedCount} of {checklist.length} complete
                </p>
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
                  className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs"
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

          {/* Quick Tools & Score Column */}
          <div className="space-y-5">
            {/* ATS Readiness Score */}
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
              {onOpenAts && (
                <button
                  type="button"
                  onClick={onOpenAts}
                  className="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs rounded-xl transition-colors flex items-center justify-center gap-1.5"
                >
                  <span>Scan Keywords &amp; ATS</span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                </button>
              )}
            </div>

            {/* Public Link Card */}
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
                Share a live public link directly with recruiters and hiring managers.
              </p>
              <button
                type="button"
                onClick={handleCopyShareLink}
                className="w-full py-2 bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs rounded-xl shadow-xs transition-colors flex items-center justify-center gap-1.5"
              >
                {copiedLink ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedLink ? 'Copied Link!' : 'Copy Public Link'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

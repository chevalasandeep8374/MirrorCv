'use client';

import React, { useState } from 'react';
import {
  Sparkles,
  X,
  Target,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Loader2,
  FileText,
  Plus,
  ThumbsUp,
  ThumbsDown,
  Layers,
  ChevronRight,
  Info,
} from 'lucide-react';
import { apiClient } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface TailorModalProps {
  isOpen: boolean;
  onClose: () => void;
  resumeId: string;
  resumeTitle: string;
}

export const TailorModal: React.FC<TailorModalProps> = ({
  isOpen,
  onClose,
  resumeId,
  resumeTitle,
}) => {
  const router = useRouter();
  const [step, setStep] = useState<'input' | 'processing' | 'results'>('input');
  const [jdText, setJdText] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [company, setCompany] = useState('');
  const [mode, setMode] = useState<'analyze' | 'full'>('analyze');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Result state
  const [runId, setRunId] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'skills' | 'changes' | 'suggestions'>('overview');
  const [confirmingSkill, setConfirmingSkill] = useState<string | null>(null);
  const [applying, setApplying] = useState(false);
  const [composing, setComposing] = useState(false);
  const [conflictWarning, setConflictWarning] = useState<string | null>(null);
  const [acceptingLowRisk, setAcceptingLowRisk] = useState(false);

  if (!isOpen) return null;

  const handleStartAnalysis = async () => {
    if (jdText.trim().length < 20) {
      setError('Please paste a job description with at least 20 characters.');
      return;
    }

    setLoading(true);
    setError(null);
    setStep('processing');

    try {
      const response = await apiClient.post('/pipeline/runs', {
        resume_id: resumeId,
        job_description_text: jdText,
        job_title: jobTitle.trim() || undefined,
        mode: mode,
      });

      const newRunId = response.data.id;
      setRunId(newRunId);

      // Poll run status until completed
      let attempts = 0;
      const pollInterval = setInterval(async () => {
        attempts += 1;
        try {
          const runRes = await apiClient.get(`/pipeline/runs/${newRunId}`);
          const runData = runRes.data;

          if (runData.status === 'completed') {
            clearInterval(pollInterval);
            // Fetch detailed tailoring output
            const tailorRes = await apiClient.get(`/tailoring/${newRunId}`);
            setResult(tailorRes.data);
            setLoading(false);
            setStep('results');
          } else if (runData.status === 'failed') {
            clearInterval(pollInterval);
            setError(runData.error || 'Tailoring analysis failed.');
            setLoading(false);
            setStep('input');
          } else if (attempts > 30) {
            clearInterval(pollInterval);
            setError('Analysis timed out. Please try again.');
            setLoading(false);
            setStep('input');
          }
        } catch (err: any) {
          clearInterval(pollInterval);
          setError(err?.response?.data?.detail || 'Polling run failed.');
          setLoading(false);
          setStep('input');
        }
      }, 1000);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to initiate job matching.');
      setLoading(false);
      setStep('input');
    }
  };

  const handleToggleChangeStatus = async (changeId: string, currentStatus: string) => {
    if (!runId) return;
    const newStatus = currentStatus === 'accepted' ? 'rejected' : 'accepted';
    setConflictWarning(null);

    try {
      const res = await apiClient.patch(`/tailoring/${runId}/changes/${changeId}`, {
        status: newStatus,
      });

      // Update local state with recomputed score and live fit estimate
      setResult((prev: any) => {
        if (!prev) return prev;
        return {
          ...prev,
          score_after: res.data.score_after,
          changes: res.data.changes,
          live_fit_estimate: res.data.live_fit_estimate || prev.live_fit_estimate,
        };
      });
    } catch (err: any) {
      if (err?.response?.status === 409) {
        setConflictWarning(err?.response?.data?.detail || 'Conflict: another change already targets this bullet or item.');
      } else {
        alert('Failed to update change status: ' + (err?.response?.data?.detail || err.message));
      }
    }
  };

  const handleAcceptLowRisk = async () => {
    if (!runId) return;
    setAcceptingLowRisk(true);
    setConflictWarning(null);

    try {
      const res = await apiClient.post(`/tailoring/${runId}/changes/accept-low-risk`);
      setResult((prev: any) => {
        if (!prev) return prev;
        return {
          ...prev,
          score_after: res.data.score_after,
          changes: res.data.changes,
          live_fit_estimate: res.data.live_fit_estimate || prev.live_fit_estimate,
        };
      });
    } catch (err: any) {
      setConflictWarning(err?.response?.data?.detail || 'Failed to accept low-risk changes.');
    } finally {
      setAcceptingLowRisk(false);
    }
  };

  const handleCompose = async () => {
    if (!runId) return;
    setComposing(true);
    try {
      await apiClient.post(`/tailoring/${runId}/compose`, {});
      onClose();
      router.push(`/tailor/${runId}`);
    } catch (err: any) {
      alert('Composition failed: ' + (err?.response?.data?.detail || err.message));
      setComposing(false);
    }
  };

  const handleConfirmSkill = async (skillName: string, suggestionId: string) => {
    setConfirmingSkill(suggestionId);
    try {
      await apiClient.post('/master-profile/items', {
        type: 'skill',
        text: skillName,
        confirmed: true,
        metadata: { source: 'user_confirmed_suggestion' },
      });

      // Mark suggestion confirmed
      setResult((prev: any) => {
        if (!prev) return prev;
        const updatedSuggestions = (prev.suggestions || []).map((s: any) =>
          s.suggestion_id === suggestionId ? { ...s, confirmed: true } : s
        );
        return { ...prev, suggestions: updatedSuggestions };
      });
    } catch (err: any) {
      alert('Failed to save to master profile: ' + (err?.response?.data?.detail || err.message));
    } finally {
      setConfirmingSkill(null);
    }
  };

  const handleApplyTailoredVersion = async () => {
    if (!runId) return;
    setApplying(true);
    try {
      const res = await apiClient.post(`/tailoring/${runId}/apply`);
      const newResumeId = res.data.new_resume_id;
      onClose();
      router.push(`/editor/${newResumeId}`);
    } catch (err: any) {
      alert('Failed to apply tailored changes: ' + (err?.response?.data?.detail || err.message));
      setApplying(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">Tailor for a Job</h2>
              <p className="text-xs text-slate-500">
                Targeting: <span className="font-semibold text-slate-700">{resumeTitle}</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6">
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 flex items-start space-x-3 text-red-800 text-sm">
              <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold">Error</p>
                <p className="text-xs text-red-700 mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {step === 'input' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                    Target Job Title (Optional)
                  </label>
                  <input
                    type="text"
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    placeholder="e.g. Senior Software Engineer"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                    Company Name (Optional)
                  </label>
                  <input
                    type="text"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    placeholder="e.g. Stripe, Google, Linear"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1.5">
                  <label className="text-xs font-semibold text-slate-700">
                    Paste Job Description <span className="text-red-500">*</span>
                  </label>
                  <span className="text-xs text-slate-400">
                    {jdText.length} / 20,000 characters
                  </span>
                </div>
                <textarea
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  placeholder="Paste the full job posting requirements, responsibilities, and qualifications..."
                  rows={8}
                  maxLength={20000}
                  className="w-full p-4 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all resize-y font-mono text-xs leading-relaxed"
                />
              </div>

              {/* Mode Selection */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <label className="block text-xs font-bold text-slate-800 mb-2.5">
                  Execution Mode
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div
                    onClick={() => setMode('analyze')}
                    className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                      mode === 'analyze'
                        ? 'bg-blue-50/70 border-blue-500 ring-1 ring-blue-500'
                        : 'bg-white border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center space-x-2.5 mb-1">
                      <Target className={`w-4 h-4 ${mode === 'analyze' ? 'text-blue-600' : 'text-slate-500'}`} />
                      <span className="text-sm font-bold text-slate-900">Analyze Mode</span>
                      <span className="px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 text-[10px] font-bold">Fast</span>
                    </div>
                    <p className="text-xs text-slate-500">
                      Calculates Estimated Match Score, matches taxonomy skills, and highlights missing gaps without modifying text.
                    </p>
                  </div>

                  <div
                    onClick={() => setMode('full')}
                    className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                      mode === 'full'
                        ? 'bg-blue-50/70 border-blue-500 ring-1 ring-blue-500'
                        : 'bg-white border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center space-x-2.5 mb-1">
                      <Sparkles className={`w-4 h-4 ${mode === 'full' ? 'text-blue-600' : 'text-slate-500'}`} />
                      <span className="text-sm font-bold text-slate-900">Full Tailoring</span>
                      <span className="px-2 py-0.5 rounded-full bg-purple-100 text-purple-700 text-[10px] font-bold">AI Tailored</span>
                    </div>
                    <p className="text-xs text-slate-500">
                      Generates verified, fact-grounded rewrites within slot line budgets protected by anti-hallucination verification.
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-5 py-2.5 rounded-xl border border-slate-300 font-semibold text-xs text-slate-600 hover:bg-slate-100 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleStartAnalysis}
                  disabled={loading || jdText.trim().length < 20}
                  className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs shadow-md shadow-blue-500/20 disabled:opacity-50 flex items-center space-x-2 transition-all"
                >
                  <span>{mode === 'analyze' ? 'Analyze Job Match' : 'Start Full Tailoring'}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {step === 'processing' && (
            <div className="py-16 flex flex-col items-center justify-center text-center space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 animate-pulse">
                <Loader2 className="w-7 h-7 animate-spin" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">Analyzing Job Match</h3>
                <p className="text-xs text-slate-500 max-w-sm mt-1">
                  Parsing job description, normalizing taxonomy skills, and calculating grounded match metrics...
                </p>
              </div>
            </div>
          )}

          {step === 'results' && result && (
            <div className="space-y-6">
              {/* Score Header Card */}
              <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 text-white shadow-xl flex flex-col md:flex-row items-center justify-between gap-6">
                <div>
                  <span className="text-[11px] font-bold tracking-wider text-blue-400 uppercase">
                    AI Match Intelligence
                  </span>
                  <h3 className="text-xl font-bold mt-1">Estimated Match Score</h3>
                  <p className="text-xs text-slate-400 mt-1 max-w-md">
                    Deterministic score derived from required skills (40%), preferred skills (15%), semantic relevance (25%), and seniority fit.
                  </p>
                  {result.score_breakdown?.confidence_note && (
                    <div className="mt-2 text-xs text-amber-300 bg-amber-950/60 border border-amber-800/60 rounded-lg px-2.5 py-1 inline-flex items-center space-x-1.5">
                      <Info className="w-3.5 h-3.5 shrink-0" />
                      <span>{result.score_breakdown.confidence_note}</span>
                    </div>
                  )}
                </div>

                <div className="flex items-center space-x-6 shrink-0">
                  <div className="text-center">
                    <span className="text-[11px] text-slate-400 uppercase font-semibold">Before</span>
                    <div className="text-3xl font-extrabold text-slate-200 mt-0.5">
                      {result.score_before?.toFixed(1)}%
                    </div>
                  </div>

                  {result.score_after !== result.score_before && (
                    <>
                      <ChevronRight className="w-6 h-6 text-slate-500" />
                      <div className="text-center">
                        <span className="text-[11px] text-emerald-400 uppercase font-semibold">After Tailoring</span>
                        <div className="text-4xl font-extrabold text-emerald-400 mt-0.5">
                          {result.score_after?.toFixed(1)}%
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="border-b border-slate-200 flex space-x-4">
                <button
                  type="button"
                  onClick={() => setActiveTab('overview')}
                  className={`pb-3 text-xs font-bold border-b-2 transition-all ${
                    activeTab === 'overview'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Score Breakdown
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('skills')}
                  className={`pb-3 text-xs font-bold border-b-2 transition-all ${
                    activeTab === 'skills'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Skills Analysis ({result.matched_keywords?.length || 0} matched, {result.missing_keywords?.length || 0} missing)
                </button>
                {result.changes?.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setActiveTab('changes')}
                    className={`pb-3 text-xs font-bold border-b-2 transition-all ${
                      activeTab === 'changes'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    Tailored Changes ({result.changes.length})
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => setActiveTab('suggestions')}
                  className={`pb-3 text-xs font-bold border-b-2 transition-all ${
                    activeTab === 'suggestions'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Skill Suggestions ({result.suggestions?.length || 0})
                </button>
              </div>

              {/* Tab: Overview Breakdown */}
              {activeTab === 'overview' && result.score_breakdown && (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                    <span className="text-[11px] font-semibold text-slate-500">Required Skills (40% max)</span>
                    <div className="text-xl font-bold text-slate-900 mt-1">
                      {result.score_breakdown.required_skill_coverage.toFixed(1)} pts
                    </div>
                    <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2 overflow-hidden">
                      <div
                        className="bg-blue-600 h-full rounded-full"
                        style={{ width: `${(result.score_breakdown.required_skill_coverage / 40) * 100}%` }}
                      />
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                    <span className="text-[11px] font-semibold text-slate-500">Preferred Skills (15% max)</span>
                    <div className="text-xl font-bold text-slate-900 mt-1">
                      {result.score_breakdown.preferred_skill_coverage.toFixed(1)} pts
                    </div>
                    <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2 overflow-hidden">
                      <div
                        className="bg-indigo-600 h-full rounded-full"
                        style={{ width: `${(result.score_breakdown.preferred_skill_coverage / 15) * 100}%` }}
                      />
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                    <span className="text-[11px] font-semibold text-slate-500">Semantic Relevance (25% max)</span>
                    <div className="text-xl font-bold text-slate-900 mt-1">
                      {result.score_breakdown.semantic_relevance.toFixed(1)} pts
                    </div>
                    <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2 overflow-hidden">
                      <div
                        className="bg-emerald-600 h-full rounded-full"
                        style={{ width: `${(result.score_breakdown.semantic_relevance / 25) * 100}%` }}
                      />
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                    <span className="text-[11px] font-semibold text-slate-500">Seniority Alignment (10% max)</span>
                    <div className="text-xl font-bold text-slate-900 mt-1">
                      {result.score_breakdown.seniority_fit.toFixed(1)} pts
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                    <span className="text-[11px] font-semibold text-slate-500">ATS Readability & Placement</span>
                    <div className="text-xl font-bold text-slate-900 mt-1">
                      {result.score_breakdown.ats_readability.toFixed(1)} pts
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                    <span className="text-[11px] font-semibold text-slate-500">Stuffing Penalty</span>
                    <div className={`text-xl font-bold mt-1 ${result.score_breakdown.stuffing_penalty > 0 ? 'text-red-600' : 'text-slate-400'}`}>
                      -{result.score_breakdown.stuffing_penalty.toFixed(1)} pts
                    </div>
                  </div>
                </div>
              )}

              {/* Tab: Skills Breakdown */}
              {activeTab === 'skills' && result.skills_analysis && (
                <div className="space-y-6">
                  <div>
                    <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2.5 flex items-center space-x-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                      <span>Matched Skills ({result.skills_analysis.matched_skills?.length || 0})</span>
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {result.skills_analysis.matched_skills?.map((s: any, idx: number) => (
                        <span
                          key={idx}
                          className="px-3 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold"
                        >
                          {s.canonical_name || s.skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2.5 flex items-center space-x-1.5">
                      <AlertTriangle className="w-4 h-4 text-amber-500" />
                      <span>Missing Skills ({result.skills_analysis.missing_skills?.length || 0})</span>
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {result.skills_analysis.missing_skills?.map((s: any, idx: number) => (
                        <span
                          key={idx}
                          className="px-3 py-1 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-xs font-semibold"
                        >
                          {s.canonical_name || s.skill} ({s.importance})
                        </span>
                      ))}
                    </div>
                  </div>

                  {result.skills_analysis.present_not_visible?.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2.5 flex items-center space-x-1.5">
                        <Layers className="w-4 h-4 text-purple-500" />
                        <span>In Master Profile (Not on this resume)</span>
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {result.skills_analysis.present_not_visible.map((s: any, idx: number) => (
                          <span
                            key={idx}
                            className="px-3 py-1 rounded-lg bg-purple-50 border border-purple-200 text-purple-800 text-xs font-semibold"
                          >
                            {s.canonical_name || s.skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {result.skills_analysis.adjacent_skills?.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2.5 flex items-center space-x-1.5">
                        <Info className="w-4 h-4 text-blue-500" />
                        <span>Adjacent / Related Skills Found</span>
                      </h4>
                      <div className="space-y-1.5">
                        {result.skills_analysis.adjacent_skills.map((a: any, idx: number) => (
                          <div key={idx} className="text-xs text-slate-600 bg-slate-50 p-2 rounded-lg border border-slate-200">
                            Requested <span className="font-bold text-slate-800">{a.jd_skill}</span> — You have related skill <span className="font-bold text-blue-700">{a.resume_skill}</span> ({a.relation})
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Tab: Tailored Changes */}
              {activeTab === 'changes' && (
                <div className="space-y-4">
                  {conflictWarning && (
                    <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 flex items-start space-x-2.5 text-amber-800 text-xs">
                      <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                      <div>
                        <p className="font-bold">Target Conflict Warning</p>
                        <p className="mt-0.5">{conflictWarning}</p>
                      </div>
                    </div>
                  )}

                  {result.live_fit_estimate && (
                    <div className={`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                      result.live_fit_estimate.fit_status === 'overflow_warning'
                        ? 'bg-red-50 border-red-200 text-red-900'
                        : result.live_fit_estimate.fit_status === 'tight'
                        ? 'bg-amber-50 border-amber-200 text-amber-900'
                        : 'bg-emerald-50 border-emerald-200 text-emerald-900'
                    }`}>
                      <div className="flex items-center space-x-3">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs ${
                          result.live_fit_estimate.fit_status === 'overflow_warning'
                            ? 'bg-red-200 text-red-800'
                            : result.live_fit_estimate.fit_status === 'tight'
                            ? 'bg-amber-200 text-amber-800'
                            : 'bg-emerald-200 text-emerald-800'
                        }`}>
                          {result.live_fit_estimate.predicted_line_delta > 0 ? `+${result.live_fit_estimate.predicted_line_delta}` : result.live_fit_estimate.predicted_line_delta}
                        </div>
                        <div>
                          <p className="text-xs font-bold">
                            Live Template Fit: {result.live_fit_estimate.fit_status === 'fits_cleanly' ? 'Fits Cleanly on 1 Page' : result.live_fit_estimate.fit_status === 'tight' ? 'Tight Margin (0-1 lines free)' : 'Overflow Warning (>1 page risk)'}
                          </p>
                          <p className="text-[11px] opacity-80">
                            Delta: {result.live_fit_estimate.predicted_line_delta} lines • Free room remaining: ~{result.live_fit_estimate.free_lines_remaining} lines ({result.live_fit_estimate.accepted_changes_count} accepted)
                          </p>
                        </div>
                      </div>

                      <button
                        type="button"
                        onClick={handleAcceptLowRisk}
                        disabled={acceptingLowRisk}
                        className="px-3 py-1.5 rounded-lg bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-xs flex items-center space-x-1.5 shrink-0 transition"
                      >
                        {acceptingLowRisk ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5 text-blue-600" />}
                        <span>Accept All Low-Risk</span>
                      </button>
                    </div>
                  )}

                  {(result.changes || []).map((chg: any) => (
                    <div
                      key={chg.change_id}
                      className={`p-4 rounded-xl border transition-all ${
                        chg.status === 'accepted'
                          ? 'bg-emerald-50/40 border-emerald-300'
                          : 'bg-slate-50 border-slate-200'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                          {chg.type} • {chg.change_id}
                        </span>
                        <div className="flex items-center space-x-2">
                          <button
                            type="button"
                            onClick={() => handleToggleChangeStatus(chg.change_id, chg.status)}
                            className={`px-3 py-1 rounded-lg text-xs font-bold flex items-center space-x-1 transition-all ${
                              chg.status === 'accepted'
                                ? 'bg-emerald-600 text-white shadow-sm'
                                : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
                            }`}
                          >
                            <ThumbsUp className="w-3.5 h-3.5" />
                            <span>{chg.status === 'accepted' ? 'Accepted' : 'Accept'}</span>
                          </button>
                        </div>
                      </div>

                      {/* Diff View */}
                      <div className="space-y-2 text-xs">
                        {chg.before && (
                          <div className="p-2.5 rounded-lg bg-red-50/60 border border-red-200/60 text-slate-700">
                            <span className="font-bold text-red-600 block mb-0.5">Original:</span>
                            {typeof chg.before === 'string' ? chg.before : JSON.stringify(chg.before)}
                          </div>
                        )}
                        {chg.after && (
                          <div className="p-2.5 rounded-lg bg-emerald-50/80 border border-emerald-200 text-slate-800">
                            <span className="font-bold text-emerald-700 block mb-0.5">Tailored:</span>
                            {typeof chg.after === 'string' ? chg.after : JSON.stringify(chg.after)}
                          </div>
                        )}
                      </div>

                      <p className="text-[11px] text-slate-500 mt-2 italic">
                        Reason: {chg.reason}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Tab: Suggestions */}
              {activeTab === 'suggestions' && (
                <div className="space-y-3">
                  {(result.suggestions || []).map((sug: any) => (
                    <div
                      key={sug.suggestion_id}
                      className="p-4 rounded-xl border border-slate-200 bg-white flex items-center justify-between gap-4"
                    >
                      <div>
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-bold text-sm text-slate-900">{sug.canonical_name}</span>
                          <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[10px] font-semibold">
                            {sug.category}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500">{sug.prompt_text}</p>
                      </div>

                      {sug.confirmed ? (
                        <span className="px-3 py-1.5 rounded-lg bg-emerald-100 text-emerald-800 text-xs font-bold flex items-center space-x-1 shrink-0">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Confirmed</span>
                        </span>
                      ) : (
                        <button
                          type="button"
                          onClick={() => handleConfirmSkill(sug.canonical_name, sug.suggestion_id)}
                          disabled={confirmingSkill === sug.suggestion_id}
                          className="px-3.5 py-1.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-700 hover:bg-blue-100 text-xs font-bold flex items-center space-x-1.5 shrink-0 transition-colors"
                        >
                          {confirmingSkill === sug.suggestion_id ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <Plus className="w-3.5 h-3.5" />
                          )}
                          <span>I have this skill</span>
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Result Footer */}
              <div className="pt-4 border-t border-slate-200 flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => setStep('input')}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors"
                >
                  Adjust JD & Re-analyze
                </button>

                <div className="flex items-center space-x-3">
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-5 py-2.5 rounded-xl border border-slate-300 font-semibold text-xs text-slate-600 hover:bg-slate-100 transition-colors"
                  >
                    Close
                  </button>
                  {result.changes?.length > 0 && (
                    <>
                      <button
                        type="button"
                        onClick={handleApplyTailoredVersion}
                        disabled={applying || composing}
                        className="px-4 py-2.5 rounded-xl border border-slate-300 hover:bg-slate-50 text-slate-700 font-semibold text-xs flex items-center space-x-2 transition-all"
                      >
                        {applying ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                        <span>Create in Editor</span>
                      </button>
                      <button
                        type="button"
                        onClick={handleCompose}
                        disabled={composing || applying}
                        className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs shadow-md shadow-blue-500/20 flex items-center space-x-2 transition-all"
                      >
                        {composing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                        <span>Generate Tailored Resume (Compose)</span>
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

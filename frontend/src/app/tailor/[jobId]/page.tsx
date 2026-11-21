'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import {
  ArrowLeft,
  Download,
  FileDown,
  Edit3,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Loader2,
  Sparkles,
  Columns,
  Sliders,
  ShieldCheck,
  AlertCircle,
  Info,
  X,
  Scissors,
} from 'lucide-react';
import PdfCompareSlider from '@/components/tailor/PdfCompareSlider';
import { CompositionResult, CompositionStatus } from '@/types/composition';
import { supabase } from '@/lib/supabase';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface TailoringChange {
  id: string;
  section_id?: string;
  item_id?: string;
  bullet_id?: string;
  target_slot_id?: string;
  original_text?: string;
  new_text?: string;
  reason?: string;
  risk_level?: 'low' | 'medium' | 'high';
  status?: 'proposed' | 'accepted' | 'rejected';
  accepted?: boolean;
}

interface TailoringData {
  job_id?: string;
  run_id?: string;
  template_id?: string;
  match_score_before?: { total_score?: number };
  match_score_after?: { total_score?: number };
  changes?: TailoringChange[];
  skills_missing?: string[];
  warnings?: string[];
  fidelity_tier?: string;
  fidelity_score?: number;
  tailored_docx_path?: string;
  tailored_content?: Record<string, unknown>;
}

export default function TailoredResultPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = (params?.jobId as string) || '';

  // Main state
  const [composition, setComposition] = useState<CompositionResult | null>(null);
  const [tailoringData, setTailoringData] = useState<TailoringData | null>(null);
  const [loading, setLoading] = useState(true);
  const [togglingChangeId, setTogglingChangeId] = useState<string | null>(null);
  const [openingEditor, setOpeningEditor] = useState(false);
  const [acknowledgingOverflow, setAcknowledgingOverflow] = useState(false);
  const [removingBullet, setRemovingBullet] = useState(false);
  const [composing, setComposing] = useState(false);
  const [pdfTimestamp, setPdfTimestamp] = useState(Date.now());
  const [viewMode, setViewMode] = useState<'side-by-side' | 'slider'>('side-by-side');

  // Modals
  const [showIntegrityModal, setShowIntegrityModal] = useState(false);
  const [userAcknowledged, setUserAcknowledged] = useState(false);

  const fetchData = useCallback(async () => {
    if (!jobId) return;
    setLoading(true);

    try {
      // 1. Try to fetch composition first
      try {
        const compRes = await apiClient.get<CompositionResult>(`/compositions/${jobId}`);
        if (compRes.data && compRes.data.status) {
          setComposition(compRes.data);
        }
      } catch {
        // Not a direct composition ID, or composition not created yet
      }

      // 2. Try to fetch tailoring job/run data
      try {
        const tailorRes = await apiClient.get<TailoringData>(`/tailor/${jobId}`);
        if (tailorRes.data) {
          setTailoringData(tailorRes.data);
        }
      } catch {
        try {
          const runRes = await apiClient.get<TailoringData>(`/tailoring/${jobId}`);
          if (runRes.data) {
            setTailoringData(runRes.data);
          }
        } catch {
          // Tailoring endpoints fallback
        }
      }
    } catch (err) {
      console.error('Failed to load job data', err);
    } finally {
      setLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Handle Accept / Reject of individual changes
  const handleToggleChange = async (changeId: string, currentAccepted: boolean) => {
    setTogglingChangeId(changeId);
    try {
      // Update in Phase C review flow
      const targetStatus = !currentAccepted ? 'accepted' : 'rejected';
      const runId = composition?.run_id || tailoringData?.run_id || jobId;

      try {
        await apiClient.patch(`/tailoring/${runId}/changes/${changeId}`, {
          status: targetStatus,
        });
      } catch {
        // Fallback to Phase 2 toggle endpoint
        await apiClient.post(`/tailor/${jobId}/change/${changeId}`, {
          accepted: !currentAccepted,
        });
      }

      // Refresh job data
      await fetchData();
      setPdfTimestamp(Date.now());
    } catch (err) {
      console.error('Failed to toggle change', err);
    } finally {
      setTogglingChangeId(null);
    }
  };

  // Trigger Run 2 Composition
  const handleTriggerCompose = async (confirmedRemovals?: string[]) => {
    const runId = composition?.run_id || tailoringData?.run_id || jobId;
    setComposing(true);
    try {
      const payload = confirmedRemovals ? { confirmed_bullet_removals: confirmedRemovals } : {};
      const res = await apiClient.post<CompositionResult>(`/tailoring/${runId}/compose`, payload);
      setComposition(res.data);
      setPdfTimestamp(Date.now());
      setUserAcknowledged(false);
    } catch (err) {
      console.error('Failed to run composition', err);
    } finally {
      setComposing(false);
    }
  };

  // Handle Acknowledge Overflow
  const handleAcknowledgeOverflow = async () => {
    const compId = composition?.composition_id || jobId;
    setAcknowledgingOverflow(true);
    try {
      const res = await apiClient.post<CompositionResult>(`/compositions/${compId}/acknowledge-overflow`);
      setComposition(res.data);
      setUserAcknowledged(true);
    } catch (err) {
      console.error('Failed to acknowledge overflow', err);
    } finally {
      setAcknowledgingOverflow(false);
    }
  };

  // Handle "Remove Lowest-Relevance Bullet" to fit template
  const handleRemoveLowestRelevanceBullet = async () => {
    const overflowing = composition?.overflow_report?.overflowing_slots || [];
    let candidateId = overflowing[0];

    // If no slot name in overflow report, pick the lowest-priority change
    if (!candidateId && tailoringData?.changes) {
      const activeChanges = tailoringData.changes.filter(
        (c) => c.status === 'accepted' || c.accepted !== false
      );
      if (activeChanges.length > 0) {
        candidateId = activeChanges[activeChanges.length - 1].bullet_id || activeChanges[activeChanges.length - 1].id;
      }
    }

    if (!candidateId) {
      candidateId = 'bullet_last';
    }

    setRemovingBullet(true);
    try {
      await handleTriggerCompose([candidateId]);
    } finally {
      setRemovingBullet(false);
    }
  };

  // Handle "Open in Editor"
  const handleOpenInEditor = async () => {
    const finalContent = composition?.final_content || tailoringData?.tailored_content;
    if (!finalContent) return;
    setOpeningEditor(true);

    try {
      let extractedStyle: Record<string, unknown> = {};
      const templateId = tailoringData?.template_id;
      if (templateId) {
        try {
          const tplRes = await apiClient.get(`/templates/${templateId}/analysis`);
          extractedStyle = tplRes.data.style || {};
        } catch {
          // Ignore style extraction error
        }
      }

      const createRes = await apiClient.post<{ id: string }>('/resumes', {
        title: `Tailored Resume (${new Date().toLocaleDateString()})`,
        content: finalContent,
        style: extractedStyle,
      });

      router.push(`/editor/${createRes.data.id}`);
    } catch (err) {
      console.error('Failed to open in editor', err);
      setOpeningEditor(false);
    }
  };

  if (loading && !composition && !tailoringData) {
    const handleDownloadFile = async (url: string, filename: string) => {
    try {
      const { data } = await supabase.auth.getSession();
      const token = data?.session?.access_token;
      const res = await fetch(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error(`Download failed with status ${res.status}`);
      const blob = await res.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (e) {
      console.error('Download error:', e);
      alert('Failed to download file. Please try again.');
    }
  };

  return (
      <div className="flex h-screen items-center justify-center bg-slate-50 text-slate-500 font-sans text-sm">
        <Loader2 className="w-6 h-6 animate-spin mr-2" />
        <span>Loading tailored resume results...</span>
      </div>
    );
  }

  // Derive scores and status
  const scoreBefore = tailoringData?.match_score_before?.total_score || 0;
  const scoreAfter = tailoringData?.match_score_after?.total_score || 0;
  const changes = tailoringData?.changes || [];
  const missingSkills = tailoringData?.skills_missing || [];
  const warnings = composition?.warnings || tailoringData?.warnings || [];
  const fidelityScore = composition?.fidelity_score ?? tailoringData?.fidelity_score ?? 99.0;
  const status: CompositionStatus = composition?.status || 'ready';

  const docxFile = composition?.output_files?.find((f) => f.format === 'docx' || f.kind === 'tailored');
  const pdfFile = composition?.output_files?.find((f) => f.format === 'pdf');

  const docxDownloadUrl = docxFile?.download_url || `${API_BASE_URL}/api/tailor/${jobId}/docx`;
  const pdfDownloadUrl = pdfFile?.download_url || `${API_BASE_URL}/api/tailor/${jobId}/pdf`;
  const originalPdfUrl = `${API_BASE_URL}/api/tailor/${jobId}/original-pdf`;

  // Download blocked logic
  const isIntegrityFailed = composition?.integrity_report?.passed === false || status === 'failed';
  const isLayoutChanged = status === 'layout_changed';
  const isDocxDownloadDisabled = isIntegrityFailed || (isLayoutChanged && !userAcknowledged && !docxFile?.download_url);

  const handleDownloadFile = async (url: string, filename: string) => {
    try {
      const { data } = await supabase.auth.getSession();
      const token = data?.session?.access_token;
      const res = await fetch(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error(`Download failed with status ${res.status}`);
      const blob = await res.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (e) {
      console.error('Download error:', e);
      alert('Failed to download file. Please try again.');
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-slate-100 overflow-hidden select-none">
      {/* 1. Top Navbar */}
      <header className="h-14 border-b border-slate-200 bg-white px-6 flex items-center justify-between z-20 flex-shrink-0">
        <div className="flex items-center space-x-3">
          <Link
            href="/tailor"
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex items-center space-x-2">
            <span className="font-bold text-slate-900 text-sm">
              Tailoring Results
            </span>

            {/* Template Integrity Badge */}
            {composition?.integrity_report ? (
              composition.integrity_report.passed ? (
                <button
                  type="button"
                  onClick={() => setShowIntegrityModal(true)}
                  className="inline-flex items-center space-x-1 text-xs px-2.5 py-0.5 rounded-full font-bold bg-emerald-50 text-emerald-700 border border-emerald-300 hover:bg-emerald-100 transition"
                  title="Click to view verified template invariants"
                >
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Integrity Verified</span>
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => setShowIntegrityModal(true)}
                  className="inline-flex items-center space-x-1 text-xs px-2.5 py-0.5 rounded-full font-bold bg-rose-50 text-rose-700 border border-rose-300 hover:bg-rose-100 transition animate-pulse"
                  title="Click to view integrity violations"
                >
                  <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
                  <span>Integrity Failed</span>
                </button>
              )
            ) : (
              <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold">
                Fidelity Match Active
              </span>
            )}

            {fidelityScore != null && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-semibold border border-slate-200">
                {fidelityScore.toFixed(1)}% Fidelity
              </span>
            )}
          </div>
        </div>

        {/* Center: Match Score Improvement Widget & View Toggle */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3 bg-slate-50 border border-slate-200 px-3 py-1 rounded-xl text-xs">
            <span className="text-slate-500">Estimated Match:</span>
            {scoreBefore > 0 && (
              <>
                <span className="font-bold text-slate-600 line-through">{scoreBefore}%</span>
                <span className="text-slate-400">→</span>
              </>
            )}
            <span className="font-extrabold text-emerald-600 text-sm flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5" />
              <span>{scoreAfter > 0 ? `${scoreAfter}%` : 'High'}</span>
            </span>
            {scoreAfter > scoreBefore && (
              <span className="text-[11px] text-emerald-700 font-semibold bg-emerald-100/60 px-1.5 py-0.5 rounded">
                +{scoreAfter - scoreBefore}% boost
              </span>
            )}
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200 text-xs font-semibold">
            <button
              onClick={() => setViewMode('side-by-side')}
              className={`px-2.5 py-1 rounded-md transition flex items-center space-x-1.5 ${
                viewMode === 'side-by-side'
                  ? 'bg-white text-slate-900 shadow-2xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Columns className="w-3.5 h-3.5" />
              <span>Side-by-Side</span>
            </button>
            <button
              onClick={() => setViewMode('slider')}
              className={`px-2.5 py-1 rounded-md transition flex items-center space-x-1.5 ${
                viewMode === 'slider'
                  ? 'bg-white text-slate-900 shadow-2xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>Compare Slider</span>
            </button>
          </div>
        </div>

        {/* Right Action Buttons */}
        <div className="flex items-center space-x-2">
          {/* Download DOCX (Blocked on Integrity Failure or Unacknowledged Layout Overflow) */}
          {isDocxDownloadDisabled ? (
            <div className="relative group">
              <button
                disabled
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 border border-slate-200 bg-slate-100 text-slate-400 font-semibold text-xs rounded-lg cursor-not-allowed opacity-75"
              >
                <Download className="w-3.5 h-3.5 text-slate-400" />
                <span>Download DOCX</span>
              </button>
              <div className="absolute right-0 top-full mt-1 hidden group-hover:block z-30 w-64 p-2 bg-slate-900 text-white text-[11px] rounded shadow-lg">
                {isIntegrityFailed
                  ? 'DOCX download blocked: Template integrity verification failed. Template formatting must be preserved.'
                  : 'Layout overflow detected: Please review and acknowledge overflow or shorten content below.'}
              </div>
            </div>
          ) : (
            <button
              onClick={() => handleDownloadFile(docxDownloadUrl, `tailored_resume_${jobId}.docx`)}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs rounded-lg shadow-sm transition cursor-pointer"
            >
              <Download className="w-3.5 h-3.5 text-slate-500" />
              <span>Download DOCX</span>
            </button>
          )}

          {/* Download PDF */}
          <button
            onClick={() => handleDownloadFile(pdfDownloadUrl, `tailored_resume_${jobId}.pdf`)}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs rounded-lg shadow-sm transition cursor-pointer"
          >
            <FileDown className="w-3.5 h-3.5 text-slate-500" />
            <span>Download PDF</span>
          </button>

          {/* Open in Editor */}
          <button
            onClick={handleOpenInEditor}
            disabled={openingEditor}
            className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg shadow-sm transition disabled:opacity-50"
          >
            {openingEditor ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Edit3 className="w-3.5 h-3.5" />
            )}
            <span>Open in Editor</span>
          </button>
        </div>
      </header>

      {/* 2. Layout Fit Alert Banner (Status: layout_changed) */}
      {isLayoutChanged && !userAcknowledged && (
        <div className="bg-amber-50 border-b border-amber-300 px-6 py-2.5 flex items-center justify-between text-xs text-amber-900 z-10 flex-shrink-0 shadow-xs">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
            <div>
              <span className="font-bold">Layout Fit Notice: </span>
              <span>
                Tailored content caused the document page count to increase from{' '}
                <strong className="underline">{composition?.page_count_before || 1}</strong> to{' '}
                <strong className="underline">{composition?.page_count_after || 2}</strong> pages.
              </span>
              {composition?.overflow_report?.overflowing_slots?.length ? (
                <span className="text-amber-700 text-[11px] ml-1">
                  (Overflow in slot: {composition.overflow_report.overflowing_slots.join(', ')})
                </span>
              ) : null}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleRemoveLowestRelevanceBullet}
              disabled={removingBullet || composing}
              className="inline-flex items-center space-x-1 px-3 py-1 rounded-lg bg-white border border-amber-300 text-amber-800 font-semibold hover:bg-amber-100 transition shadow-2xs"
            >
              {removingBullet ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <Scissors className="w-3 h-3 text-amber-600" />
              )}
              <span>Remove Lowest-Relevance Bullet</span>
            </button>

            <button
              onClick={handleAcknowledgeOverflow}
              disabled={acknowledgingOverflow}
              className="inline-flex items-center space-x-1 px-3 py-1 rounded-lg bg-amber-600 hover:bg-amber-700 text-white font-semibold transition shadow-2xs"
            >
              {acknowledgingOverflow ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <CheckCircle2 className="w-3 h-3" />
              )}
              <span>Acknowledge & Enable Download</span>
            </button>
          </div>
        </div>
      )}

      {/* Integrity Failure Warning Banner */}
      {isIntegrityFailed && (
        <div className="bg-rose-50 border-b border-rose-300 px-6 py-2 flex items-center justify-between text-xs text-rose-900 z-10 flex-shrink-0">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
            <span className="font-bold">Template Integrity Failure:</span>
            <span>
              The output violated template invariants. DOCX download is blocked to guarantee your master template formatting is never compromised.
            </span>
          </div>
          <button
            onClick={() => setShowIntegrityModal(true)}
            className="underline font-semibold hover:text-rose-950"
          >
            View Violation Report
          </button>
        </div>
      )}

      {/* General Warnings Banner */}
      {warnings.length > 0 && !isLayoutChanged && !isIntegrityFailed && (
        <div className="bg-slate-50 border-b border-slate-200 px-6 py-1.5 flex items-center space-x-2 text-xs text-slate-700 flex-shrink-0">
          <Info className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
          <span className="font-bold">Notice:</span>
          <span>{warnings.join(' · ')}</span>
        </div>
      )}

      {/* 3. Main Body: Split View (PDF Comparison on Left/Center, Changes on Right) */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left & Center: PDF Viewer Mode */}
        {viewMode === 'slider' ? (
          <PdfCompareSlider
            originalPdfUrl={originalPdfUrl}
            tailoredPdfUrl={`${pdfDownloadUrl}?t=${pdfTimestamp}`}
          />
        ) : (
          <div className="flex-1 flex divide-x divide-slate-300 overflow-hidden bg-slate-200/50">
            {/* Original Uploaded PDF */}
            <div className="flex-1 flex flex-col h-full overflow-hidden">
              <div className="h-9 bg-slate-100 border-b border-slate-200 px-4 flex items-center justify-between text-xs font-bold text-slate-600">
                <span>Original Uploaded Resume</span>
                <span className="text-[10px] uppercase font-semibold text-slate-400">Master Template</span>
              </div>
              <div className="flex-1 w-full h-full bg-slate-300">
                <iframe
                  src={originalPdfUrl}
                  className="w-full h-full border-none"
                  title="Original Resume PDF"
                />
              </div>
            </div>

            {/* Tailored Fidelity Output PDF */}
            <div className="flex-1 flex flex-col h-full overflow-hidden">
              <div className="h-9 bg-emerald-50 border-b border-emerald-200 px-4 flex items-center justify-between text-xs font-bold text-emerald-800">
                <span className="flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Tailored Resume (Identical Format Output)</span>
                </span>
                <span className="text-[10px] uppercase font-semibold text-emerald-600">Fidelity PDF</span>
              </div>
              <div className="flex-1 w-full h-full bg-slate-300">
                <iframe
                  src={`${pdfDownloadUrl}?t=${pdfTimestamp}`}
                  className="w-full h-full border-none"
                  title="Tailored Resume PDF"
                />
              </div>
            </div>
          </div>
        )}

        {/* Right Drawer: Change List & Missing Keywords */}
        <aside className="w-[420px] flex-shrink-0 bg-white border-l border-slate-200 flex flex-col h-full overflow-hidden">
          {/* Header */}
          <div className="p-3.5 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
            <div>
              <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Tailored Changes ({changes.length})
              </h2>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Review accepted modifications before composing
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                {changes.filter((c) => c.status === 'accepted' || c.accepted !== false).length} Active
              </span>
            </div>
          </div>

          {/* Scrollable Change Cards */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3.5">
            {/* Missing Skills Alert */}
            {missingSkills.length > 0 && (
              <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-xs">
                <div className="flex items-center space-x-1.5 font-bold text-amber-800 mb-1">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Skills Not Present in Your Background</span>
                </div>
                <p className="text-[11px] text-amber-700 mb-2 leading-relaxed">
                  Per strict anti-hallucination guardrails, these JD skills were NOT fabricated into your resume:
                </p>
                <div className="flex flex-wrap gap-1">
                  {missingSkills.map((sk: string, i: number) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 bg-white border border-amber-300 text-amber-800 rounded font-medium text-[10px]"
                    >
                      {sk}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* List of Changes */}
            {changes.map((chg, i) => {
              const isAccepted = chg.status === 'accepted' || (chg.status !== 'rejected' && chg.accepted !== false);
              const isToggling = togglingChangeId === chg.id;

              const handleDownloadFile = async (url: string, filename: string) => {
    try {
      const { data } = await supabase.auth.getSession();
      const token = data?.session?.access_token;
      const res = await fetch(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error(`Download failed with status ${res.status}`);
      const blob = await res.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (e) {
      console.error('Download error:', e);
      alert('Failed to download file. Please try again.');
    }
  };

  return (
                <div
                  key={chg.id || i}
                  className={`p-3.5 rounded-xl border transition-all text-xs ${
                    isAccepted
                      ? 'border-slate-200 bg-white shadow-sm'
                      : 'border-slate-200 bg-slate-50 opacity-60'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-slate-700 text-[11px] uppercase tracking-wide">
                      {chg.section_id || 'Achievement'}
                    </span>

                    {/* Accept / Reject Toggle Button */}
                    <button
                      type="button"
                      onClick={() => handleToggleChange(chg.id, isAccepted)}
                      disabled={isToggling}
                      className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg text-xs font-semibold transition ${
                        isAccepted
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100'
                          : 'bg-slate-200 text-slate-600 hover:bg-slate-300'
                      }`}
                    >
                      {isToggling ? (
                        <Loader2 className="w-3 h-3 animate-spin" />
                      ) : isAccepted ? (
                        <>
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          <span>Accepted</span>
                        </>
                      ) : (
                        <>
                          <XCircle className="w-3 h-3 text-slate-500" />
                          <span>Rejected</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* Tailored Result */}
                  <div className="mb-2">
                    <span className="text-[10px] font-bold text-emerald-700 uppercase">
                      Tailored Output
                    </span>
                    <p className="font-medium text-slate-900 mt-0.5 leading-snug">
                      {chg.new_text}
                    </p>
                  </div>

                  {/* Original Text */}
                  {chg.original_text && (
                    <div className="mb-2 pt-2 border-t border-slate-100">
                      <span className="text-[10px] font-semibold text-slate-400 uppercase">
                        Original
                      </span>
                      <p className="text-slate-500 line-through text-[11px] mt-0.5 leading-snug">
                        {chg.original_text}
                      </p>
                    </div>
                  )}

                  {/* Reason */}
                  {chg.reason && (
                    <div className="mt-2 pt-1.5 border-t border-slate-100 text-[11px] text-blue-700 bg-blue-50/50 p-2 rounded-lg">
                      <span className="font-bold">Reason: </span>
                      <span>{chg.reason}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </aside>
      </div>

      {/* 4. Template Integrity Report Modal */}
      {showIntegrityModal && composition?.integrity_report && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg border border-slate-200 overflow-hidden flex flex-col max-h-[85vh]">
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div className="flex items-center space-x-2">
                <ShieldCheck
                  className={`w-5 h-5 ${
                    composition.integrity_report.passed ? 'text-emerald-600' : 'text-rose-600'
                  }`}
                />
                <h3 className="font-bold text-slate-900 text-sm">
                  Template Integrity Verification Report
                </h3>
              </div>
              <button
                onClick={() => setShowIntegrityModal(false)}
                className="p-1 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-200/50"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 text-xs">
              <div
                className={`p-3 rounded-xl border ${
                  composition.integrity_report.passed
                    ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                    : 'bg-rose-50 border-rose-200 text-rose-900'
                }`}
              >
                <div className="font-bold text-sm mb-1">
                  {composition.integrity_report.passed
                    ? 'All Template Invariants Passed'
                    : 'Integrity Verification Failed'}
                </div>
                <p className="text-[11px]">
                  {composition.integrity_report.passed
                    ? 'The output document was byte-verified: fonts, sizes, margins, namespaces, spacing, and container boundaries are 100% identical to your uploaded master template.'
                    : 'One or more template invariants were violated during composition. Download is blocked to protect formatting.'}
                </p>
              </div>

              {/* Violations List */}
              {composition.integrity_report.violations.length > 0 && (
                <div>
                  <h4 className="font-bold text-rose-800 uppercase tracking-wider text-[10px] mb-1.5">
                    Detected Violations ({composition.integrity_report.violations.length})
                  </h4>
                  <ul className="space-y-1 bg-rose-50/50 p-3 rounded-lg border border-rose-200">
                    {composition.integrity_report.violations.map((v, i) => (
                      <li key={i} className="flex items-start space-x-1.5 text-rose-700 text-[11px]">
                        <XCircle className="w-3.5 h-3.5 text-rose-500 flex-shrink-0 mt-0.5" />
                        <span>{v}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Checked Invariants */}
              <div>
                <h4 className="font-bold text-slate-700 uppercase tracking-wider text-[10px] mb-2">
                  Verified Invariants
                </h4>
                <div className="space-y-2">
                  {composition.integrity_report.invariants_checked.map((inv, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded-lg border border-slate-200 bg-slate-50 flex items-start justify-between"
                    >
                      <div>
                        <div className="font-semibold text-slate-800">{inv.name}</div>
                        {inv.details && (
                          <div className="text-[11px] text-slate-500 mt-0.5">{inv.details}</div>
                        )}
                      </div>
                      {inv.passed ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 ml-2" />
                      ) : (
                        <XCircle className="w-4 h-4 text-rose-600 flex-shrink-0 ml-2" />
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Byte Identical Non-XML Archive Parts */}
              {composition.integrity_report.byte_identical_parts &&
                composition.integrity_report.byte_identical_parts.length > 0 && (
                  <div>
                    <h4 className="font-bold text-slate-700 uppercase tracking-wider text-[10px] mb-1">
                      Byte-Identical Parts (SHA-256 Verified)
                    </h4>
                    <p className="text-[11px] text-slate-500 leading-relaxed font-mono bg-slate-100 p-2 rounded border border-slate-200 break-all">
                      {composition.integrity_report.byte_identical_parts.join(', ')}
                    </p>
                  </div>
                )}
            </div>

            <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 flex justify-end">
              <button
                onClick={() => setShowIntegrityModal(false)}
                className="px-4 py-1.5 bg-slate-800 hover:bg-slate-900 text-white font-semibold rounded-lg text-xs"
              >
                Close Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import {
  FileText,
  ArrowLeft,
  Download,
  FileDown,
  Edit3,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Loader2,
  Sparkles,
  RefreshCw,
} from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function TailoredResultPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params?.jobId as string;

  const [job, setJob] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [togglingChangeId, setTogglingChangeId] = useState<string | null>(null);
  const [openingEditor, setOpeningEditor] = useState(false);
  const [pdfTimestamp, setPdfTimestamp] = useState(Date.now());

  const fetchJob = useCallback(async () => {
    if (!jobId) return;
    try {
      const res = await apiClient.get(`/tailor/${jobId}`);
      setJob(res.data);
    } catch (err) {
      console.error('Failed to load job', err);
    } finally {
      setLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    fetchJob();
  }, [fetchJob]);

  // Handle Accept / Reject of individual changes
  const handleToggleChange = async (changeId: string, currentAccepted: boolean) => {
    setTogglingChangeId(changeId);
    try {
      await apiClient.post(`/tailor/${jobId}/change/${changeId}`, {
        accepted: !currentAccepted,
      });
      // Refresh job data and trigger PDF re-render
      await fetchJob();
      setPdfTimestamp(Date.now());
    } catch (err) {
      console.error('Failed to toggle change', err);
    } finally {
      setTogglingChangeId(null);
    }
  };

  // Handle "Open in Editor" (creates Phase 1 resume and navigates to editor)
  const handleOpenInEditor = async () => {
    if (!job || !job.tailored_content) return;
    setOpeningEditor(true);
    try {
      // Fetch template analysis to get extracted style tokens
      const tplRes = await apiClient.get(`/templates/${job.template_id}/analysis`);
      const extractedStyle = tplRes.data.style;

      // Create new resume in Phase 1 database
      const createRes = await apiClient.post('/resumes', {
        title: `Tailored Resume (${new Date().toLocaleDateString()})`,
        content: job.tailored_content,
        style: extractedStyle,
      });

      router.push(`/editor/${createRes.data.id}`);
    } catch (err) {
      console.error('Failed to open in editor', err);
      setOpeningEditor(false);
    }
  };

  if (loading || !job) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 text-slate-500 font-sans text-sm">
        <Loader2 className="w-6 h-6 animate-spin mr-2" />
        <span>Loading tailored resume results...</span>
      </div>
    );
  }

  const scoreBefore = job.match_score_before?.total_score || 0;
  const scoreAfter = job.match_score_after?.total_score || 0;
  const changes = job.changes || [];
  const missingSkills = job.skills_missing || [];

  return (
    <div className="h-screen w-screen flex flex-col bg-slate-100 overflow-hidden select-none">
      {/* 1. Top Navbar */}
      <header className="h-14 border-b border-slate-200 bg-white px-6 flex items-center justify-between z-20 flex-shrink-0">
        <div className="flex items-center space-x-3">
          <Link
            href="/"
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex items-center space-x-2">
            <span className="font-bold text-slate-900 text-sm">
              Tailoring Job Results
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold">
              Fidelity Match Active
            </span>
          </div>
        </div>

        {/* Center: Match Score Improvement Widget */}
        <div className="flex items-center space-x-3 bg-slate-50 border border-slate-200 px-3 py-1 rounded-xl text-xs">
          <span className="text-slate-500">JD Match:</span>
          <span className="font-bold text-slate-600 line-through">{scoreBefore}%</span>
          <span className="text-slate-400">→</span>
          <span className="font-extrabold text-emerald-600 text-sm flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>{scoreAfter}%</span>
          </span>
          <span className="text-[11px] text-emerald-700 font-semibold bg-emerald-100/60 px-1.5 py-0.2 rounded">
            +{scoreAfter - scoreBefore}% boost
          </span>
        </div>

        {/* Right Action Buttons */}
        <div className="flex items-center space-x-2">
          {/* Download DOCX */}
          <a
            href={`${API_BASE_URL}/api/tailor/${jobId}/docx`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs rounded-lg shadow-sm transition"
          >
            <Download className="w-3.5 h-3.5 text-slate-500" />
            <span>Download DOCX</span>
          </a>

          {/* Download PDF */}
          <a
            href={`${API_BASE_URL}/api/tailor/${jobId}/pdf`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs rounded-lg shadow-sm transition"
          >
            <FileDown className="w-3.5 h-3.5 text-slate-500" />
            <span>Download PDF</span>
          </a>

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

      {/* 2. Main Body: Split View (PDF Comparison on Left/Center, Changes & Score on Right) */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left & Center: Side-by-Side PDF Viewer */}
        <div className="flex-1 flex divide-x divide-slate-300 overflow-hidden bg-slate-200/50">
          {/* Original Uploaded PDF */}
          <div className="flex-1 flex flex-col h-full overflow-hidden">
            <div className="h-9 bg-slate-100 border-b border-slate-200 px-4 flex items-center justify-between text-xs font-bold text-slate-600">
              <span>Original Uploaded Resume</span>
              <span className="text-[10px] uppercase font-semibold text-slate-400">Master Template</span>
            </div>
            <div className="flex-1 w-full h-full bg-slate-300">
              <iframe
                src={`${API_BASE_URL}/api/tailor/${jobId}/original-pdf`}
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
                src={`${API_BASE_URL}/api/tailor/${jobId}/pdf?t=${pdfTimestamp}`}
                className="w-full h-full border-none"
                title="Tailored Resume PDF"
              />
            </div>
          </div>
        </div>

        {/* Right Drawer: Change List & Missing Keywords */}
        <aside className="w-[420px] flex-shrink-0 bg-white border-l border-slate-200 flex flex-col h-full overflow-hidden">
          {/* Tabs / Header */}
          <div className="p-3.5 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
            <div>
              <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Tailored Changes ({changes.length})
              </h2>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Toggle changes to re-render fidelity output
              </p>
            </div>
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
              {changes.filter((c: any) => c.accepted !== false).length} Active
            </span>
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
            {changes.map((chg: any, i: number) => {
              const isAccepted = chg.accepted !== false;
              const isToggling = togglingChangeId === chg.id;

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
                  <div className="mb-2 pt-2 border-t border-slate-100">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase">
                      Original
                    </span>
                    <p className="text-slate-500 line-through text-[11px] mt-0.5 leading-snug">
                      {chg.original_text}
                    </p>
                  </div>

                  {/* Reason */}
                  <div className="mt-2 pt-1.5 border-t border-slate-100 text-[11px] text-blue-700 bg-blue-50/50 p-2 rounded-lg">
                    <span className="font-bold">Reason: </span>
                    <span>{chg.reason}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </aside>
      </div>
    </div>
  );
}

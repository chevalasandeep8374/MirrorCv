'use client';

import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  X,
  CheckCircle2,
  AlertTriangle,
  Info,
  Search,
  Sparkles,
  ArrowRight,
  Target,
  FileCheck,
} from 'lucide-react';
import { useResume } from '@/context/ResumeContext';
import { apiClient } from '@/lib/api';

interface AtsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface AtsCheckItem {
  category: string;
  name: string;
  passed: boolean;
  severity: 'critical' | 'warning' | 'info';
  message: string;
  suggestion?: string | null;
}

interface AtsStats {
  total_bullets: number;
  bullets_with_metrics: number;
  metrics_percentage: number;
  strong_verbs_count: number;
  weak_verbs_count: number;
  average_bullet_chars: number;
}

interface MatchScore {
  total_score: number;
  matched_keywords: string[];
  missing_keywords: string[];
  coverage_ratio: number;
  explanation: string;
}

interface AtsResponse {
  overall_score: number;
  grade: string;
  summary: string;
  checks: AtsCheckItem[];
  stats: AtsStats;
  jd_match?: MatchScore | null;
}

export const AtsModal: React.FC<AtsModalProps> = ({ isOpen, onClose }) => {
  const { content, style, resumeId } = useResume();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AtsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [jdText, setJdText] = useState('');
  const [showJdInput, setShowJdInput] = useState(false);

  const runAnalysis = async (targetJd?: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.post('/ats/analyze', {
        resume_id: resumeId || undefined,
        content: content,
        style: style,
        job_description: targetJd || (jdText.trim() ? jdText.trim() : undefined),
      });
      setResult(res.data);
    } catch {
      setError('Failed to complete ATS analysis. Please verify your connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      runAnalysis();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    if (score >= 70) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (score >= 50) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-rose-600 bg-rose-50 border-rose-200';
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 bg-gradient-to-r from-slate-900 to-slate-800 text-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <div>
              <h2 className="font-bold text-base leading-tight">ATS Readiness & Compliance Audit</h2>
              <p className="text-[11px] text-slate-300">
                Rule-based parsing analysis across headings, active voice, quantifiable impact, and JD match
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

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {loading && !result ? (
            <div className="py-16 text-center space-y-3">
              <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-xs text-slate-500 font-medium">Running 15+ automated ATS compliance checks...</p>
            </div>
          ) : result ? (
            <>
              {/* Top Score Banner */}
              <div className="flex items-center gap-5 p-4 rounded-xl border bg-slate-50 border-slate-200">
                <div
                  className={`w-20 h-20 rounded-2xl border flex flex-col items-center justify-center font-black shrink-0 ${getScoreColor(
                    result.overall_score
                  )}`}
                >
                  <span className="text-2xl leading-none">{result.overall_score}</span>
                  <span className="text-[10px] font-bold tracking-wider mt-0.5">/ 100</span>
                  <span className="text-xs font-bold">{result.grade}</span>
                </div>

                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-bold text-slate-900 leading-tight">
                    {result.summary}
                  </h3>
                  <div className="grid grid-cols-3 gap-2 mt-2 pt-2 border-t border-slate-200 text-[11px] text-slate-600">
                    <div>
                      <span className="font-bold text-slate-800">{result.stats.metrics_percentage}%</span> metrics
                    </div>
                    <div>
                      <span className="font-bold text-slate-800">{result.stats.strong_verbs_count}</span> active verbs
                    </div>
                    <div>
                      <span className="font-bold text-slate-800">{result.stats.total_bullets}</span> total bullets
                    </div>
                  </div>
                </div>
              </div>

              {/* JD Keyword Match Section */}
              <div className="p-4 bg-blue-50/50 border border-blue-200 rounded-xl space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Target className="w-4 h-4 text-blue-600" />
                    <span className="text-xs font-bold text-slate-900">Job Description Alignment</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setShowJdInput(!showJdInput)}
                    className="text-xs text-blue-600 hover:text-blue-700 font-semibold"
                  >
                    {showJdInput ? 'Hide JD Box' : result.jd_match ? 'Change Target JD' : '+ Check Against Target JD'}
                  </button>
                </div>

                {showJdInput && (
                  <div className="space-y-2 pt-1">
                    <textarea
                      rows={3}
                      value={jdText}
                      onChange={(e) => setJdText(e.target.value)}
                      placeholder="Paste job description requirements and qualifications here..."
                      className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
                    />
                    <button
                      type="button"
                      disabled={loading || !jdText.trim()}
                      onClick={() => runAnalysis(jdText)}
                      className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50"
                    >
                      <Search className="w-3.5 h-3.5" />
                      <span>{loading ? 'Matching...' : 'Calculate Keyword Match'}</span>
                    </button>
                  </div>
                )}

                {result.jd_match && (
                  <div className="space-y-2 pt-1 border-t border-blue-200/60">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-700">{result.jd_match.explanation}</span>
                      <span className="font-bold text-blue-700 bg-blue-100 px-2 py-0.5 rounded">
                        {result.jd_match.total_score}% Match
                      </span>
                    </div>

                    {result.jd_match.missing_keywords.length > 0 && (
                      <div className="text-[11px] text-slate-600">
                        <span className="font-bold text-rose-600">Missing Target Keywords: </span>
                        {result.jd_match.missing_keywords.slice(0, 8).join(', ')}
                        {result.jd_match.missing_keywords.length > 8 && ` +${result.jd_match.missing_keywords.length - 8} more`}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Checklist Breakdown */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Compliance Checklist ({result.checks.filter((c) => c.passed).length} of {result.checks.length} passed)
                </h4>

                <div className="space-y-2">
                  {result.checks.map((chk, idx) => (
                    <div
                      key={idx}
                      className={`p-3 rounded-lg border text-xs transition-colors ${
                        chk.passed
                          ? 'border-slate-200 bg-white'
                          : chk.severity === 'critical'
                          ? 'border-rose-300 bg-rose-50/50'
                          : 'border-amber-300 bg-amber-50/50'
                      }`}
                    >
                      <div className="flex items-start gap-2.5">
                        {chk.passed ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                        ) : chk.severity === 'critical' ? (
                          <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                        ) : (
                          <Info className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                        )}

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-800">{chk.name}</span>
                            <span
                              className={`text-[10px] font-semibold px-2 py-0.2 rounded uppercase ${
                                chk.passed
                                  ? 'bg-emerald-100 text-emerald-800'
                                  : chk.severity === 'critical'
                                  ? 'bg-rose-100 text-rose-800'
                                  : 'bg-amber-100 text-amber-800'
                              }`}
                            >
                              {chk.passed ? 'Passed' : chk.severity}
                            </span>
                          </div>
                          <p className="text-slate-600 mt-0.5 leading-relaxed">{chk.message}</p>
                          {chk.suggestion && (
                            <div className="mt-1.5 p-2 bg-white/80 rounded border border-slate-200/60 text-[11px] text-slate-700 flex items-start gap-1.5 font-medium">
                              <Sparkles className="w-3.5 h-3.5 text-blue-600 shrink-0 mt-0.5" />
                              <span>{chk.suggestion}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            error && <div className="p-3 bg-rose-50 text-rose-700 text-xs rounded-lg">{error}</div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
          <span className="text-[11px] text-slate-500 font-medium">
            MirrorCV ATS Engine adheres to Jobscan and standard resume OCR specifications.
          </span>
          <button
            type="button"
            onClick={onClose}
            className="text-xs font-semibold bg-slate-800 hover:bg-slate-900 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

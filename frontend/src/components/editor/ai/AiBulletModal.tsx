'use client';

import React, { useState } from 'react';
import { Sparkles, X, Check, AlertCircle, ArrowRight } from 'lucide-react';
import { apiClient } from '@/lib/api';

interface AiBulletModalProps {
  initialText: string;
  isOpen: boolean;
  onClose: () => void;
  onAccept: (newText: string) => void;
}

export const AiBulletModal: React.FC<AiBulletModalProps> = ({
  initialText,
  isOpen,
  onClose,
  onAccept,
}) => {
  const [action, setAction] = useState<
    'improve' | 'shorten' | 'add_impact' | 'fix_grammar' | 'change_tone'
  >('improve');
  const [tone, setTone] = useState<'formal' | 'executive' | 'technical' | 'casual'>('formal');
  const [metricAnswer, setMetricAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [suggestedText, setSuggestedText] = useState<string | null>(null);
  const [diffSummary, setDiffSummary] = useState<string | null>(null);
  const [clarification, setClarification] = useState<string | null>(null);
  const [stats, setStats] = useState<{ tokens: number; cost: number } | null>(null);

  if (!isOpen) return null;

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setSuggestedText(null);
    setDiffSummary(null);
    setClarification(null);

    try {
      const res = await apiClient.post('/ai/bullet-action', {
        text: initialText,
        action,
        tone: action === 'change_tone' ? tone : undefined,
        metric_answer: action === 'add_impact' && metricAnswer.trim() ? metricAnswer.trim() : undefined,
      });

      setSuggestedText(res.data.suggested_text);
      setDiffSummary(res.data.diff_summary);
      setClarification(res.data.clarification_needed);
      setStats({
        tokens: res.data.tokens_used,
        cost: res.data.estimated_cost,
      });
    } catch (err: unknown) {
      const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } };
      if (axiosErr.response?.status === 429) {
        setError(axiosErr.response.data?.detail || 'Daily AI request limit reached. Resets at midnight UTC.');
      } else {
        setError('Failed to generate AI suggestion. Please check your network and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-amber-300" />
            <h3 className="font-bold text-base">AI Bullet Assistant</h3>
          </div>
          <button
            onClick={onClose}
            className="text-white/80 hover:text-white p-1 rounded-lg hover:bg-white/10"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-4">
          {/* Original Text */}
          <div>
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
              Original Bullet
            </label>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-800 leading-relaxed font-mono">
              {initialText}
            </div>
          </div>

          {/* Action selection */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
              Choose Action
            </label>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <button
                type="button"
                onClick={() => setAction('improve')}
                className={`py-2 px-3 rounded-lg border text-left font-medium transition-all ${
                  action === 'improve'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-slate-200 hover:border-slate-300 text-slate-700'
                }`}
              >
                ✨ Elevate & Polish
              </button>
              <button
                type="button"
                onClick={() => setAction('shorten')}
                className={`py-2 px-3 rounded-lg border text-left font-medium transition-all ${
                  action === 'shorten'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-slate-200 hover:border-slate-300 text-slate-700'
                }`}
              >
                ✂️ Shorten & Tighten
              </button>
              <button
                type="button"
                onClick={() => setAction('add_impact')}
                className={`py-2 px-3 rounded-lg border text-left font-medium transition-all ${
                  action === 'add_impact'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-slate-200 hover:border-slate-300 text-slate-700'
                }`}
              >
                📈 Add Measurable Impact
              </button>
              <button
                type="button"
                onClick={() => setAction('fix_grammar')}
                className={`py-2 px-3 rounded-lg border text-left font-medium transition-all ${
                  action === 'fix_grammar'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-slate-200 hover:border-slate-300 text-slate-700'
                }`}
              >
                🔤 Fix Grammar & Tense
              </button>
              <button
                type="button"
                onClick={() => setAction('change_tone')}
                className={`py-2 px-3 rounded-lg border text-left font-medium transition-all col-span-2 ${
                  action === 'change_tone'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-slate-200 hover:border-slate-300 text-slate-700'
                }`}
              >
                🎯 Change Tone ({tone})
              </button>
            </div>
          </div>

          {/* Tone picker if change_tone */}
          {action === 'change_tone' && (
            <div className="flex gap-2">
              {(['formal', 'executive', 'technical', 'casual'] as const).map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setTone(t)}
                  className={`text-xs px-2.5 py-1 rounded-md capitalize font-medium ${
                    tone === t
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          )}

          {/* Metric input if add_impact */}
          {action === 'add_impact' && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 space-y-2">
              <label className="text-xs font-semibold text-amber-900 block">
                Quantifiable Result / Metric:
              </label>
              <input
                type="text"
                value={metricAnswer}
                onChange={(e) => setMetricAnswer(e.target.value)}
                placeholder="e.g. 40% faster latency, 15,000 active users, $50k cost savings"
                className="w-full text-xs px-3 py-2 border border-amber-300 rounded-md focus:outline-none focus:ring-1 focus:ring-amber-500 bg-white"
              />
              <p className="text-[11px] text-amber-700">
                To guarantee zero hallucinated numbers, provide your real metric or leave blank for a clarifying prompt.
              </p>
            </div>
          )}

          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {clarification && (
            <div className="p-3 bg-amber-50 border border-amber-300 rounded-lg text-xs text-amber-800 space-y-1">
              <div className="font-bold flex items-center gap-1.5">
                <AlertCircle className="w-4 h-4 text-amber-600" />
                <span>Clarification Needed:</span>
              </div>
              <p>{clarification}</p>
            </div>
          )}

          {suggestedText && (
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
                Suggested Revision
              </label>
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-900 leading-relaxed font-medium">
                {suggestedText}
              </div>

              {diffSummary && (
                <div className="bg-slate-900 text-slate-200 p-2.5 rounded-lg text-[11px] font-mono whitespace-pre-wrap leading-relaxed">
                  {diffSummary}
                </div>
              )}

              {stats && (
                <div className="flex items-center justify-between text-[10px] text-slate-400">
                  <span>Tokens: {stats.tokens}</span>
                  <span>Estimated Cost: ${stats.cost.toFixed(5)}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
          <button
            type="button"
            onClick={onClose}
            className="text-xs font-semibold text-slate-600 hover:text-slate-800 px-3 py-1.5"
          >
            Cancel
          </button>

          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={loading}
              onClick={handleGenerate}
              className="text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-1.5 disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{loading ? 'Generating...' : 'Run AI Action'}</span>
            </button>

            {suggestedText && (
              <button
                type="button"
                onClick={() => {
                  onAccept(suggestedText);
                  onClose();
                }}
                className="text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-1.5"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Accept Revision</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

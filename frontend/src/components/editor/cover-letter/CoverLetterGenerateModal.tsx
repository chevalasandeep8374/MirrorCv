'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import { Sparkles, X, Wand2, ShieldCheck, ArrowRight } from 'lucide-react';

interface CoverLetterGenerateModalProps {
  resumeId: string;
  isOpen: boolean;
  onClose: () => void;
  onGenerated?: (newDocId: string) => void;
}

export const CoverLetterGenerateModal: React.FC<CoverLetterGenerateModalProps> = ({
  resumeId,
  isOpen,
  onClose,
  onGenerated,
}) => {
  const router = useRouter();
  const [jobTitle, setJobTitle] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [tone, setTone] = useState<'formal' | 'friendly' | 'concise'>('formal');
  const [length, setLength] = useState<'short' | 'medium' | 'detailed'>('medium');
  const [generating, setGenerating] = useState(false);

  if (!isOpen) return null;

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);

    try {
      const res = await apiClient.post<{ document_id: string }>(
        `/resumes/${resumeId}/generate-cover-letter`,
        {
          job_title: jobTitle.trim() || undefined,
          company_name: companyName.trim() || undefined,
          job_description: jobDescription.trim() || undefined,
          tone,
          length,
        }
      );

      onClose();
      if (onGenerated) {
        onGenerated(res.data.document_id);
      } else {
        router.push(`/editor/${res.data.document_id}`);
      }
    } catch (err) {
      console.error('Failed to generate cover letter:', err);
      alert('Could not generate cover letter. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95 select-none">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2">
            <div className="p-1.5 rounded-lg bg-blue-50 text-blue-600">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-sm">
                Generate Cover Letter from Resume
              </h3>
              <p className="text-[11px] text-slate-500">
                Grounds all claims strictly in your verified resume achievements.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-800 rounded-lg hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleGenerate} className="mt-4 space-y-3.5 text-xs">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                Target Company *
              </label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="e.g. Stripe, Google, Linear"
                className="w-full px-3 py-1.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                Target Role / Job Title
              </label>
              <input
                type="text"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="e.g. Principal Distributed Engineer"
                className="w-full px-3 py-1.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-700 mb-1">
              Job Description (Optional keywords match)
            </label>
            <textarea
              rows={3}
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste job posting text here to emphasize matching competencies..."
              className="w-full px-3 py-1.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none leading-relaxed"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                Tone
              </label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value as any)}
                className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white"
              >
                <option value="formal">Formal & Dignified</option>
                <option value="friendly">Warm & Engaging</option>
                <option value="concise">Concise & Direct</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                Length
              </label>
              <select
                value={length}
                onChange={(e) => setLength(e.target.value as any)}
                className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white"
              >
                <option value="short">Short (3 Paragraphs)</option>
                <option value="medium">Standard (4 Paragraphs)</option>
                <option value="detailed">Detailed (In-depth)</option>
              </select>
            </div>
          </div>

          {/* Anti-Hallucination Guardrail Badge */}
          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center gap-2 text-slate-600">
            <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
            <span className="text-[11px]">
              <strong>Strict Fact-Check Guardrail:</strong> Zero invented employers, dates, or credentials.
            </span>
          </div>

          {/* Buttons */}
          <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-1.5 text-xs text-slate-600 hover:text-slate-900"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={generating || !companyName.trim()}
              className="px-4 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 disabled:opacity-50 flex items-center gap-1.5 shadow-sm"
            >
              {generating ? (
                <>
                  <Wand2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Generating Draft...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Generate Cover Letter</span>
                  <ArrowRight className="w-3 h-3 ml-0.5" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

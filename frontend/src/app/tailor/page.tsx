'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import {
  FileText,
  Upload,
  ArrowRight,
  Loader2,
  CheckCircle2,
  Sparkles,
  ArrowLeft,
  FileCheck,
  AlertCircle,
} from 'lucide-react';

export default function NewTailoredResumePage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState('');
  const [loading, setLoading] = useState(false);
  const [stepMessage, setStepMessage] = useState('');
  const [error, setError] = useState<string | null>(null);

  const pipelineStages = [
    'Parsing & fingerprinting DOCX template formatting',
    'Classifying paragraph roles and section hierarchies',
    'Analyzing target job description and required competencies',
    'Tailoring achievements with strict character budgets',
    'Writing fidelity DOCX and deep-copy XML paragraph cloning',
    'Converting PDF and running multi-page fit checks',
    'Computing keyword coverage score before & after',
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      if (!selected.name.toLowerCase().endsWith('.docx')) {
        setError('Only .docx files are supported.');
        return;
      }
      setFile(selected);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please upload your original DOCX resume.');
      return;
    }
    if (!jdText.trim()) {
      setError('Please paste the target job description.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 1. Upload DOCX template
      setStepMessage('Uploading and fingerprinting DOCX template...');
      const formData = new FormData();
      formData.append('file', file);

      const uploadRes = await apiClient.post('/templates/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const templateId = uploadRes.data.id;

      // 2. Submit Tailoring Job
      setStepMessage('Launching tailoring pipeline in background...');
      const tailorRes = await apiClient.post('/tailor', {
        template_id: templateId,
        jd_text: jdText,
      });
      const jobId = tailorRes.data.job_id;

      // 3. Poll for pipeline completion
      let stageIdx = 0;
      const interval = setInterval(async () => {
        try {
          const poll = await apiClient.get(`/tailor/${jobId}`);
          if (poll.data.status === 'completed') {
            clearInterval(interval);
            router.push(`/tailor/${jobId}`);
          } else if (poll.data.status === 'failed') {
            clearInterval(interval);
            setError(poll.data.error || 'Tailoring failed.');
            setLoading(false);
          } else {
            stageIdx = (stageIdx + 1) % pipelineStages.length;
            setStepMessage(pipelineStages[stageIdx]);
          }
        } catch (pollErr) {
          console.warn('Poll error:', pollErr);
        }
      }, 1500);

    } catch (err: any) {
      setError(err?.response?.data?.detail || 'An error occurred while uploading.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Navbar */}
      <header className="border-b border-slate-200 bg-white sticky top-0 z-20">
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Link
              href="/"
              className="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <span className="text-base font-bold text-slate-900 tracking-tight">
              Tailor Resume from Upload (Phase 2)
            </span>
          </div>
        </div>
      </header>

      {/* Main Form Body */}
      <main className="max-w-3xl mx-auto px-6 py-10 flex-1 w-full">
        <div className="mb-8">
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-blue-600" />
            <span>Generate Identical-Look Tailored Resume</span>
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Upload your master DOCX resume and paste the job description. MirrorCV preserves your runs,
            fonts, and layout in-place with zero invented facts.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {loading ? (
          /* Progress View */
          <div className="bg-white border border-slate-200 rounded-2xl p-10 text-center shadow-sm">
            <div className="w-16 h-16 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-6">
              <Loader2 className="w-8 h-8 animate-spin" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">
              Tailoring Resume in Progress...
            </h3>
            <p className="text-sm text-blue-600 font-medium animate-pulse mb-8">
              {stepMessage}
            </p>

            <div className="max-w-md mx-auto space-y-2 text-left text-xs text-slate-500">
              {pipelineStages.map((stg, i) => (
                <div key={i} className="flex items-center space-x-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />
                  <span>{stg}</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          /* Submission Form */
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Step 1: Upload DOCX */}
            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
                1. Upload Master Resume (.docx)
              </label>

              <div className="border-2 border-dashed border-slate-200 hover:border-blue-400 rounded-xl p-8 text-center transition-colors">
                <input
                  type="file"
                  id="resume-file"
                  accept=".docx"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <label htmlFor="resume-file" className="cursor-pointer flex flex-col items-center">
                  <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
                    {file ? <FileCheck className="w-6 h-6" /> : <Upload className="w-6 h-6" />}
                  </div>
                  {file ? (
                    <div>
                      <span className="font-bold text-slate-900 text-sm">{file.name}</span>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {(file.size / 1024).toFixed(1)} KB — Ready for extraction
                      </p>
                    </div>
                  ) : (
                    <div>
                      <span className="font-semibold text-blue-600 hover:underline text-sm">
                        Click to upload DOCX
                      </span>
                      <span className="text-slate-500 text-sm"> or drag and drop</span>
                      <p className="text-xs text-slate-400 mt-1">Microsoft Word documents up to 5 MB</p>
                    </div>
                  )}
                </label>
              </div>
            </div>

            {/* Step 2: Job Description Text */}
            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
                2. Target Job Description (Paste Text)
              </label>
              <textarea
                rows={8}
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Paste the job requirements, responsibilities, and qualifications here..."
                className="w-full text-xs p-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-1 focus:ring-blue-500 leading-relaxed font-sans"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl shadow-sm transition-all flex items-center justify-center space-x-2"
            >
              <span>Analyze & Tailor Resume</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}
      </main>
    </div>
  );
}

'use client';

import React, { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, X, FileText, CheckCircle2, AlertCircle, ArrowRight, Loader2, Sparkles, ShieldCheck } from 'lucide-react';
import { apiClient } from '@/lib/api';

interface ImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export const ImportModal: React.FC<ImportModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'docx' | 'json_resume' | 'linkedin'>('docx');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Result state
  const [docxResult, setDocxResult] = useState<{
    id: string;
    resume_id: string;
    fidelity_score: number;
    page_count_match: boolean;
    slots_count: number;
    sections_detected: string[];
    warnings?: string[];
  } | null>(null);

  const [importResult, setImportResult] = useState<{
    resume_id: string;
    title: string;
    mapping_report: {
      source: string;
      mapped_fields?: string[];
      unmapped_fields?: string[];
      mapped_sources?: string[];
      unmapped_sources?: string[];
      total_sections_imported: number;
    };
  } | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setImportResult(null);
    setDocxResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      if (activeTab === 'docx') {
        const res = await apiClient.post('/templates/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setDocxResult(res.data);
      } else {
        const endpoint = activeTab === 'json_resume' ? '/import/json-resume' : '/import/linkedin-zip';
        const res = await apiClient.post(endpoint, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setImportResult(res.data);
      }
      if (onSuccess) onSuccess();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setError(axiosErr.response?.data?.detail || 'Failed to process import file. Please check format.');
    } finally {
      setLoading(false);
      e.target.value = '';
    }
  };

  const getAcceptType = () => {
    if (activeTab === 'docx') return '.docx';
    if (activeTab === 'json_resume') return '.json';
    return '.zip';
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 bg-gradient-to-r from-blue-700 to-indigo-800 text-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Upload className="w-5 h-5 text-blue-200" />
            <div>
              <h2 className="font-bold text-base leading-tight">Import Resume</h2>
              <p className="text-[11px] text-blue-100">
                Agent 1 (Template Guardian) guarantees 100% layout fidelity
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

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 bg-slate-50 px-6 text-xs font-semibold text-slate-600">
          <button
            onClick={() => {
              setActiveTab('docx');
              setError(null);
              setImportResult(null);
              setDocxResult(null);
            }}
            className={`py-3 px-4 border-b-2 transition-colors ${
              activeTab === 'docx'
                ? 'border-blue-600 text-blue-600 font-bold bg-white'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            DOCX Resume (Guardian)
          </button>
          <button
            onClick={() => {
              setActiveTab('json_resume');
              setError(null);
              setImportResult(null);
              setDocxResult(null);
            }}
            className={`py-3 px-4 border-b-2 transition-colors ${
              activeTab === 'json_resume'
                ? 'border-blue-600 text-blue-600 font-bold bg-white'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            JSON Resume (.json)
          </button>
          <button
            onClick={() => {
              setActiveTab('linkedin');
              setError(null);
              setImportResult(null);
              setDocxResult(null);
            }}
            className={`py-3 px-4 border-b-2 transition-colors ${
              activeTab === 'linkedin'
                ? 'border-blue-600 text-blue-600 font-bold bg-white'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            LinkedIn Data (.zip)
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-4 overflow-y-auto">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept={getAcceptType()}
            className="hidden"
          />

          {!docxResult && !importResult ? (
            <div className="space-y-4">
              <p className="text-xs text-slate-600 leading-relaxed">
                {activeTab === 'docx'
                  ? 'Upload your existing Word resume (.docx). Agent 1 maps all slots, resolves exact fonts and character budgets, and tests fidelity.'
                  : activeTab === 'json_resume'
                  ? 'Upload a standard schema.json file from JSON Resume. All fields will be mapped to our content model.'
                  : 'Upload your LinkedIn data export ZIP. We parse Profile, Positions, Education, and Skills automatically.'}
              </p>

              <div
                onClick={() => !loading && fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                  loading
                    ? 'border-slate-300 bg-slate-50 opacity-60'
                    : 'border-blue-300 hover:border-blue-500 bg-blue-50/30 hover:bg-blue-50/60'
                }`}
              >
                {loading ? (
                  <div className="space-y-2">
                    <Loader2 className="w-8 h-8 text-blue-600 animate-spin mx-auto" />
                    <p className="text-xs font-semibold text-slate-700">
                      {activeTab === 'docx'
                        ? 'Template Guardian analyzing typography & running fidelity test...'
                        : 'Parsing and mapping resume data...'}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Upload className="w-8 h-8 text-blue-600 mx-auto" />
                    <p className="text-xs font-bold text-slate-800">
                      Click to choose {activeTab === 'docx' ? 'DOCX Resume (.docx)' : activeTab === 'json_resume' ? 'JSON Resume (.json)' : 'LinkedIn Archive (.zip)'}
                    </p>
                    <p className="text-[11px] text-slate-500">Max file size 5 MB</p>
                  </div>
                )}
              </div>

              {error && (
                <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-xs">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}
            </div>
          ) : docxResult ? (
            /* DOCX Template Guardian Result */
            <div className="space-y-4">
              <div className="flex items-center gap-2.5 p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800">
                <ShieldCheck className="w-6 h-6 text-emerald-600 shrink-0" />
                <div>
                  <h3 className="font-bold text-sm">Template Guardian Analysis Complete</h3>
                  <p className="text-xs text-emerald-700">
                    Fidelity score: <span className="font-extrabold">{docxResult.fidelity_score.toFixed(1)}%</span> • {docxResult.slots_count} slots mapped
                  </p>
                </div>
              </div>

              <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 text-xs space-y-2">
                <div className="flex justify-between">
                  <span className="text-slate-500">Page Count Match:</span>
                  <span className={`font-semibold ${docxResult.page_count_match ? 'text-emerald-600' : 'text-red-600'}`}>
                    {docxResult.page_count_match ? 'Matched (No Overflow)' : 'Page Count Mismatch'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Sections Detected:</span>
                  <span className="font-semibold text-slate-800">
                    {docxResult.sections_detected.slice(0, 4).join(', ')}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2">
                <button
                  onClick={() => {
                    setDocxResult(null);
                    setError(null);
                  }}
                  className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900"
                >
                  Import Another
                </button>
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      onClose();
                      router.push(`/templates/${docxResult.id}`);
                    }}
                    className="px-3.5 py-2 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg transition"
                  >
                    View Report
                  </button>
                  <button
                    onClick={() => {
                      onClose();
                      router.push(`/editor/${docxResult.resume_id}`);
                    }}
                    className="px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-1.5 shadow-sm transition"
                  >
                    Open in Editor
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ) : (
            /* JSON / LinkedIn Result */
            <div className="space-y-4">
              <div className="flex items-center gap-2 p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                <div>
                  <h3 className="font-bold">Import Successful!</h3>
                  <p>Created new resume: &quot;{importResult?.title}&quot;</p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2">
                <button
                  onClick={() => {
                    setImportResult(null);
                    setError(null);
                  }}
                  className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900"
                >
                  Import Another
                </button>
                <button
                  onClick={() => {
                    onClose();
                    if (importResult?.resume_id) {
                      router.push(`/editor/${importResult.resume_id}`);
                    }
                  }}
                  className="px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-1.5 shadow-sm transition"
                >
                  Open in Editor
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

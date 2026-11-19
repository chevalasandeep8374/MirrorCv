'use client';

import React, { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
  Upload,
  X,
  FileText,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Loader2,
  Sparkles,
  ShieldCheck,
  FileType,
  FileCode,
  FileArchive,
  Layers,
} from 'lucide-react';
import { apiClient } from '@/lib/api';
import { getActiveRepository } from '@/repositories';

interface ImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

type ImportTab = 'universal' | 'pdf' | 'docx' | 'json_resume' | 'linkedin';

export const ImportModal: React.FC<ImportModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<ImportTab>('universal');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Result state
  const [importedData, setImportedData] = useState<{
    resume_id: string;
    title: string;
    format: string;
    detected_sections: string[];
    total_sections: number;
    message?: string;
  } | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const getAcceptType = () => {
    switch (activeTab) {
      case 'pdf':
        return '.pdf';
      case 'docx':
        return '.docx,.doc';
      case 'json_resume':
        return '.json';
      case 'linkedin':
        return '.zip';
      case 'universal':
      default:
        return '.pdf,.docx,.doc,.json,.zip,.txt';
    }
  };

  const processFile = async (file: File) => {
    setLoading(true);
    setError(null);
    setImportedData(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // 1. Post to Universal Resume Import endpoint
      const res = await apiClient.post('/import/resume', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const data = res.data;

      // 2. Sync to active frontend repository (LocalStorage or Supabase)
      try {
        const repo = await getActiveRepository();
        await repo.create({
          id: data.resume_id,
          title: data.title || file.name.replace(/\.[^/.]+$/, ''),
          content: data.content,
          style: data.style,
          tags: ['imported', data.format || 'file'],
        });
      } catch (repoErr) {
        console.warn('Repository sync notice:', repoErr);
      }

      setImportedData({
        resume_id: data.resume_id,
        title: data.title || file.name.replace(/\.[^/.]+$/, ''),
        format: data.format || file.name.split('.').pop() || 'document',
        detected_sections: data.detected_sections || [],
        total_sections: data.total_sections || (data.detected_sections || []).length,
        message: data.message,
      });

      if (onSuccess) onSuccess();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setError(
        axiosErr.response?.data?.detail ||
          'Failed to parse resume. Please ensure the file is an unlocked PDF, DOCX, JSON, or LinkedIn ZIP.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    await processFile(file);
    e.target.value = '';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isDragging) setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (loading) return;
    const file = e.dataTransfer.files?.[0];
    if (file) {
      await processFile(file);
    }
  };

  const getFormatBadge = (fmt: string) => {
    const f = fmt.toLowerCase();
    if (f.includes('pdf')) {
      return { label: 'PDF Document', color: 'bg-red-50 text-red-700 border-red-200' };
    }
    if (f.includes('docx') || f.includes('doc')) {
      return { label: 'Word Document (DOCX)', color: 'bg-blue-50 text-blue-700 border-blue-200' };
    }
    if (f.includes('json')) {
      return { label: 'JSON Resume', color: 'bg-amber-50 text-amber-700 border-amber-200' };
    }
    if (f.includes('zip') || f.includes('linkedin')) {
      return { label: 'LinkedIn Archive (ZIP)', color: 'bg-indigo-50 text-indigo-700 border-indigo-200' };
    }
    return { label: `${fmt.toUpperCase()} File`, color: 'bg-slate-50 text-slate-700 border-slate-200' };
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-xl overflow-hidden flex flex-col max-h-[92vh]">
        {/* Header */}
        <div className="px-6 py-4 bg-gradient-to-r from-slate-950 via-slate-900 to-indigo-950 text-white flex items-center justify-between border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/10 rounded-xl backdrop-blur-md">
              <Upload className="w-5 h-5 text-blue-300" />
            </div>
            <div>
              <h2 className="font-bold text-base leading-tight">Import Existing Resume</h2>
              <p className="text-[11px] text-slate-300">
                Universal intake for PDF, Word (.docx), JSON, or LinkedIn data
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white/70 hover:text-white p-1.5 rounded-lg hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 bg-slate-50/80 px-4 text-xs font-semibold text-slate-600 overflow-x-auto">
          {[
            { id: 'universal', label: 'All Formats', icon: Sparkles },
            { id: 'pdf', label: 'PDF (.pdf)', icon: FileText },
            { id: 'docx', label: 'Word (.docx)', icon: FileType },
            { id: 'json_resume', label: 'JSON Resume', icon: FileCode },
            { id: 'linkedin', label: 'LinkedIn (.zip)', icon: FileArchive },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id as ImportTab);
                  setError(null);
                  setImportedData(null);
                }}
                className={`py-3 px-3.5 border-b-2 transition-all flex items-center gap-1.5 whitespace-nowrap cursor-pointer ${
                  isActive
                    ? 'border-primary text-primary font-bold bg-white shadow-xs'
                    : 'border-transparent hover:text-slate-900 hover:bg-slate-100/50'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-primary' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
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

          {!importedData ? (
            <div className="space-y-4">
              <div className="text-xs text-slate-600 leading-relaxed">
                {activeTab === 'universal' && (
                  <p>
                    Select or drag any existing resume. MirrorCV automatically detects format, extracts contact details, work history, skills, and projects, and formats it for pixel-perfect editing.
                  </p>
                )}
                {activeTab === 'pdf' && (
                  <p>
                    Upload any standard PDF resume. Agent 1 parses vector blocks, extracts hierarchy, contact links, and section structure.
                  </p>
                )}
                {activeTab === 'docx' && (
                  <p>
                    Upload your Microsoft Word resume (.docx). The parser maps typography, bullet levels, tables, and section hierarchies.
                  </p>
                )}
                {activeTab === 'json_resume' && (
                  <p>
                    Upload a standard JSON Resume (<code className="text-primary font-mono text-[11px]">schema.json</code>). All fields map seamlessly to our content model.
                  </p>
                )}
                {activeTab === 'linkedin' && (
                  <p>
                    Upload your LinkedIn Data Export ZIP archive. Profile, Positions, Education, and Skills CSVs are parsed automatically.
                  </p>
                )}
              </div>

              {/* Universal Drag & Drop Zone */}
              <div
                onClick={() => !loading && fileInputRef.current?.click()}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
                  isDragging
                    ? 'border-primary bg-blue-50/80 scale-[1.01] shadow-md ring-4 ring-blue-500/10'
                    : loading
                    ? 'border-slate-300 bg-slate-50 opacity-60 cursor-not-allowed'
                    : 'border-slate-300 hover:border-primary bg-slate-50/40 hover:bg-blue-50/30'
                }`}
              >
                {loading ? (
                  <div className="space-y-3 py-2">
                    <Loader2 className="w-10 h-10 text-primary animate-spin mx-auto" />
                    <div>
                      <p className="text-xs font-bold text-slate-800">
                        Analyzing and parsing resume...
                      </p>
                      <p className="text-[11px] text-slate-500 mt-1">
                        Extracting sections, contact info, and typography hierarchy
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="w-12 h-12 rounded-2xl bg-blue-50 text-primary border border-blue-200 flex items-center justify-center mx-auto shadow-xs">
                      <Upload className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-slate-900">
                        {isDragging
                          ? 'Drop your resume file here'
                          : 'Click to choose or drag & drop your resume file'}
                      </p>
                      <p className="text-[11px] text-slate-500 mt-0.5">
                        Supports PDF, Word (.docx), JSON, or LinkedIn ZIP (Max 10 MB)
                      </p>
                    </div>

                    {/* Supported Format Pills */}
                    <div className="flex flex-wrap items-center justify-center gap-1.5 pt-2">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-50 text-red-700 border border-red-200">
                        .PDF
                      </span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                        .DOCX
                      </span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                        .JSON
                      </span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                        .ZIP (LinkedIn)
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {error && (
                <div className="flex items-start gap-2.5 p-3.5 bg-red-50 border border-red-200 text-red-700 rounded-xl text-xs">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-600" />
                  <div className="leading-relaxed">
                    <span className="font-semibold block mb-0.5">Import Error</span>
                    <span>{error}</span>
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* Successful Import Result Card */
            <div className="space-y-4">
              <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl text-emerald-900 space-y-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-emerald-600 text-white rounded-xl shadow-xs">
                    <CheckCircle2 className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-sm">Resume Imported Successfully!</h3>
                    <p className="text-xs text-emerald-700">
                      Created document: &quot;<span className="font-semibold">{importedData.title}</span>&quot;
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 pt-1">
                  {(() => {
                    const badge = getFormatBadge(importedData.format);
                    return (
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${badge.color}`}
                      >
                        {badge.label}
                      </span>
                    );
                  })()}
                  <span className="text-[11px] text-emerald-700 font-medium">
                    {importedData.total_sections} section(s) identified
                  </span>
                </div>
              </div>

              {/* Detected Sections Grid */}
              {importedData.detected_sections.length > 0 && (
                <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 space-y-2">
                  <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                    Detected Resume Modules
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {importedData.detected_sections.map((sec, idx) => (
                      <span
                        key={idx}
                        className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-slate-700 shadow-2xs"
                      >
                        {sec}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => {
                    setImportedData(null);
                    setError(null);
                  }}
                  className="px-3 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900 transition"
                >
                  Import Another
                </button>
                <button
                  type="button"
                  onClick={() => {
                    onClose();
                    router.push(`/editor/${importedData.resume_id}`);
                  }}
                  className="btn-primary !text-xs !py-2.5 !px-5 shadow-btn flex items-center gap-1.5"
                >
                  <span>Open in Editor</span>
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

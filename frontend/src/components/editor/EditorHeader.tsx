'use client';

import React, { useRef, useState } from 'react';
import Link from 'next/link';
import {
  FileText,
  ArrowLeft,
  CheckCircle2,
  Clock,
  AlertCircle,
  Download,
  Upload,
  FileDown,
  Loader2,
  ZoomIn,
  ZoomOut,
  Undo2,
  Redo2,
  Sparkles,
  Layers,
  Share2,
  History,
  AlertTriangle,
  ShieldCheck,
} from 'lucide-react';
import { useResume } from '@/context/ResumeContext';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface EditorHeaderProps {
  onOpenVersions?: () => void;
  onOpenShare?: () => void;
  onOpenAi?: () => void;
  onOpenAts?: () => void;
  onOpenTailor?: () => void;
}

export const EditorHeader: React.FC<EditorHeaderProps> = ({
  onOpenVersions,
  onOpenShare,
  onOpenAi,
  onOpenAts,
  onOpenTailor,
}) => {
  const {
    resumeId,
    title,
    setTitle,
    saveStatus,
    resolveConflict,
    saveNow,
    exportContentJson,
    importContentJson,
    exportStyleJson,
    importStyleJson,
    zoom,
    setZoom,
    canUndo,
    canRedo,
    undo,
    redo,
    onePageFitActive,
    onePageFitWarning,
    toggleOnePageFit,
  } = useResume();

  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [downloadingDocx, setDownloadingDocx] = useState(false);
  const contentInputRef = useRef<HTMLInputElement>(null);
  const styleInputRef = useRef<HTMLInputElement>(null);

  const handleDownloadDocx = async () => {
    setDownloadingDocx(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/resumes/${resumeId}/export/docx`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('mirrorcv_token') || ''}`,
        },
      });

      if (!response.ok) {
        throw new Error('DOCX export failed on backend');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${title.toLowerCase().replace(/[^a-z0-9]/g, '_')}_resume.docx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Failed to export DOCX. Please try again.');
    } finally {
      setDownloadingDocx(false);
    }
  };

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/resumes/${resumeId}/export/pdf`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('mirrorcv_token') || ''}`,
        },
      });

      if (!response.ok) {
        throw new Error('PDF export failed on backend');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${title.toLowerCase().replace(/[^a-z0-9]/g, '_')}_resume.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.warn('Backend Playwright PDF error, falling back to window.print():', err);
      window.open(`/render/${resumeId}`, '_blank');
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleContentFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const parsed = JSON.parse(event.target?.result as string);
        importContentJson(parsed);
      } catch (err) {
        alert('Invalid Content JSON file.');
      }
    };
    reader.readAsText(file);
    e.target.value = '';
  };

  const handleStyleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const parsed = JSON.parse(event.target?.result as string);
        importStyleJson(parsed);
      } catch (err) {
        alert('Invalid Style JSON file.');
      }
    };
    reader.readAsText(file);
    e.target.value = '';
  };

  return (
    <header className="h-14 border-b border-slate-200 bg-white px-4 flex items-center justify-between z-30 select-none">
      {/* Hidden file inputs for JSON import */}
      <input
        type="file"
        ref={contentInputRef}
        onChange={handleContentFileUpload}
        accept=".json"
        className="hidden"
      />
      <input
        type="file"
        ref={styleInputRef}
        onChange={handleStyleFileUpload}
        accept=".json"
        className="hidden"
      />

      {/* Left: Back button + Title + Autosave */}
      <div className="flex items-center space-x-3">
        <Link
          href="/"
          className="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          title="Back to Resumes"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>

        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="font-bold text-slate-900 text-sm md:text-base bg-transparent hover:bg-slate-100 focus:bg-white focus:ring-1 focus:ring-blue-500 rounded px-2 py-0.5 border border-transparent hover:border-slate-300 focus:border-blue-500 outline-none transition-all w-48 md:w-60 truncate"
            placeholder="Untitled Resume"
          />

          {/* Autosave Indicator */}
          <div className="hidden sm:flex items-center text-xs font-medium pl-1">
            {saveStatus === 'saved' && (
              <span className="flex items-center text-emerald-600 gap-1" title="All edits autosaved">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span className="hidden md:inline">Saved</span>
              </span>
            )}
            {saveStatus === 'saving' && (
              <span className="flex items-center text-blue-600 gap-1">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span className="hidden md:inline">Saving...</span>
              </span>
            )}
            {saveStatus === 'unsaved' && (
              <span className="flex items-center text-amber-600 gap-1">
                <Clock className="w-3.5 h-3.5" />
                <span className="hidden md:inline">Unsaved</span>
              </span>
            )}
            {saveStatus === 'error' && (
              <span className="flex items-center text-rose-600 gap-1">
                <AlertCircle className="w-3.5 h-3.5" />
                <span className="hidden md:inline">Save error</span>
                <button
                  type="button"
                  onClick={() => saveNow()}
                  className="underline ml-0.5 text-xs text-rose-700 hover:text-rose-900 font-semibold"
                >
                  Retry
                </button>
              </span>
            )}
            {saveStatus === 'conflict' && (
              <span className="flex items-center text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded text-xs gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                <span className="font-medium">Cloud conflict:</span>
                <button
                  type="button"
                  onClick={() => resolveConflict('reload')}
                  className="underline hover:text-amber-900 font-semibold"
                >
                  Reload
                </button>
                <span>/</span>
                <button
                  type="button"
                  onClick={() => resolveConflict('overwrite')}
                  className="underline hover:text-amber-900 font-semibold"
                >
                  Overwrite
                </button>
              </span>
            )}
          </div>
        </div>

        {/* Undo / Redo Buttons */}
        <div className="hidden md:flex items-center space-x-0.5 pl-2 border-l border-slate-200">
          <button
            type="button"
            onClick={undo}
            disabled={!canUndo}
            className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition disabled:opacity-30 disabled:hover:bg-transparent"
            title="Undo (Ctrl+Z)"
          >
            <Undo2 className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={redo}
            disabled={!canRedo}
            className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition disabled:opacity-30 disabled:hover:bg-transparent"
            title="Redo (Ctrl+Y)"
          >
            <Redo2 className="w-4 h-4" />
          </button>
        </div>

        {/* One-Page Fit Toggle */}
        <div className="hidden lg:flex items-center pl-2">
          <button
            type="button"
            onClick={toggleOnePageFit}
            className={`px-2.5 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
              onePageFitActive
                ? 'bg-amber-100 text-amber-800 border border-amber-300'
                : 'text-slate-600 hover:bg-slate-100 border border-slate-200'
            }`}
            title="Automatically adjust font scale & spacing to fit onto exactly one page"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            <span>1-Page Fit</span>
          </button>

          {onePageFitWarning && (
            <span
              className="ml-2 flex items-center gap-1 text-[11px] text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 truncate max-w-xs"
              title={onePageFitWarning}
            >
              <AlertTriangle className="w-3 h-3 text-amber-600 shrink-0" />
              <span>{onePageFitWarning}</span>
            </span>
          )}
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center space-x-2">
        {/* Templates Gallery Link */}
        <Link
          href="/templates"
          className="hidden sm:inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-semibold"
          title="Browse Template Presets"
        >
          <Layers className="w-3.5 h-3.5 text-blue-600" />
          <span>Templates</span>
        </Link>

        {/* Tailor for Job Button */}
        {onOpenTailor && (
          <button
            type="button"
            onClick={onOpenTailor}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 text-xs font-bold shadow-sm transition"
            title="Tailor for a target Job Description"
          >
            <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
            <span>Tailor for Job</span>
          </button>
        )}

        {/* AI Assistant Button */}
        {onOpenAi && (
          <button
            type="button"
            onClick={onOpenAi}
            className="inline-flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 text-xs font-bold shadow-sm transition"
            title="AI Writing Assistant & Skills Extractor"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            <span>AI Assistant</span>
          </button>
        )}

        {/* ATS Check Button */}
        {onOpenAts && (
          <button
            type="button"
            onClick={onOpenAts}
            className="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-lg border border-emerald-300 bg-emerald-50 text-emerald-800 hover:bg-emerald-100 text-xs font-bold transition"
            title="ATS Compatibility & Formatting Check"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>ATS Check</span>
          </button>
        )}

        {/* Version History Button */}
        {onOpenVersions && (
          <button
            type="button"
            onClick={onOpenVersions}
            className="p-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 transition"
            title="Version History"
          >
            <History className="w-4 h-4" />
          </button>
        )}

        {/* Share Button */}
        {onOpenShare && (
          <button
            type="button"
            onClick={onOpenShare}
            className="p-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 transition"
            title="Public Share Link"
          >
            <Share2 className="w-4 h-4" />
          </button>
        )}

        {/* Zoom Controls */}
        <div className="hidden sm:flex items-center border border-slate-200 rounded-lg overflow-hidden bg-slate-50 text-xs font-semibold text-slate-600">
          <button
            onClick={() => setZoom((z) => Math.max(0.5, Math.round((z - 0.1) * 10) / 10))}
            className="p-1.5 hover:bg-slate-200 text-slate-700 transition"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="px-2 py-1 select-none w-11 text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={() => setZoom((z) => Math.min(1.5, Math.round((z + 0.1) * 10) / 10))}
            className="p-1.5 hover:bg-slate-200 text-slate-700 transition"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Download DOCX Button */}
        <button
          type="button"
          onClick={handleDownloadDocx}
          disabled={downloadingDocx}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 border border-slate-200 hover:border-slate-300 bg-white text-slate-700 font-semibold text-xs rounded-lg shadow-2xs transition disabled:opacity-50"
          title="Download editable Microsoft Word document"
        >
          {downloadingDocx ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-600" />
          ) : (
            <FileText className="w-3.5 h-3.5 text-blue-600" />
          )}
          <span>DOCX</span>
        </button>

        {/* Download PDF Button */}
        <button
          onClick={handleDownloadPdf}
          disabled={downloadingPdf}
          className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg shadow-sm transition disabled:opacity-50"
        >
          {downloadingPdf ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <FileDown className="w-3.5 h-3.5" />
          )}
          <span>Download PDF</span>
        </button>
      </div>
    </header>
  );
};

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
} from 'lucide-react';
import { useResume } from '@/context/ResumeContext';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const EditorHeader: React.FC = () => {
  const {
    resumeId,
    title,
    setTitle,
    saveStatus,
    exportContentJson,
    importContentJson,
    exportStyleJson,
    importStyleJson,
    zoom,
    setZoom,
  } = useResume();

  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const contentInputRef = useRef<HTMLInputElement>(null);
  const styleInputRef = useRef<HTMLInputElement>(null);

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    try {
      // Backend Playwright PDF endpoint
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
      // Fallback: Open print preview
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

      {/* Left: Back button + Title */}
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
            className="font-bold text-slate-900 text-base bg-transparent hover:bg-slate-100 focus:bg-white focus:ring-1 focus:ring-blue-500 rounded px-2 py-0.5 border border-transparent hover:border-slate-300 focus:border-blue-500 outline-none transition-all w-60"
            placeholder="Untitled Resume"
          />

          {/* Autosave Indicator */}
          <div className="flex items-center text-xs font-medium pl-2">
            {saveStatus === 'saved' && (
              <span className="flex items-center text-emerald-600 gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Saved</span>
              </span>
            )}
            {saveStatus === 'saving' && (
              <span className="flex items-center text-blue-600 gap-1">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Saving...</span>
              </span>
            )}
            {saveStatus === 'unsaved' && (
              <span className="flex items-center text-amber-600 gap-1">
                <Clock className="w-3.5 h-3.5" />
                <span>Unsaved</span>
              </span>
            )}
            {saveStatus === 'error' && (
              <span className="flex items-center text-rose-600 gap-1">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>Save error</span>
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center space-x-2">
        {/* Zoom Controls */}
        <div className="flex items-center border border-slate-200 rounded-lg overflow-hidden bg-slate-50 mr-2 text-xs font-semibold text-slate-600">
          <button
            onClick={() => setZoom((z) => Math.max(0.5, Math.round((z - 0.1) * 10) / 10))}
            className="p-1.5 hover:bg-slate-200 text-slate-700 transition"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="px-2 py-1 select-none w-12 text-center">
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

        {/* Content JSON dropdown/buttons */}
        <div className="flex items-center border border-slate-200 rounded-lg text-xs font-medium text-slate-700 divide-x divide-slate-200 bg-white">
          <button
            onClick={exportContentJson}
            className="px-2.5 py-1.5 hover:bg-slate-50 flex items-center space-x-1"
            title="Export Content JSON"
          >
            <Download className="w-3 h-3 text-slate-500" />
            <span>Content JSON</span>
          </button>
          <button
            onClick={() => contentInputRef.current?.click()}
            className="px-2 py-1.5 hover:bg-slate-50 flex items-center"
            title="Import Content JSON"
          >
            <Upload className="w-3 h-3 text-slate-500" />
          </button>
        </div>

        {/* Style JSON dropdown/buttons */}
        <div className="flex items-center border border-slate-200 rounded-lg text-xs font-medium text-slate-700 divide-x divide-slate-200 bg-white">
          <button
            onClick={exportStyleJson}
            className="px-2.5 py-1.5 hover:bg-slate-50 flex items-center space-x-1"
            title="Export Style JSON"
          >
            <Download className="w-3 h-3 text-slate-500" />
            <span>Style JSON</span>
          </button>
          <button
            onClick={() => styleInputRef.current?.click()}
            className="px-2 py-1.5 hover:bg-slate-50 flex items-center"
            title="Import Style JSON"
          >
            <Upload className="w-3 h-3 text-slate-500" />
          </button>
        </div>

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

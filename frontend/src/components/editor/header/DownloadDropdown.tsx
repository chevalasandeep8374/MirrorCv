'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useResume } from '@/context/ResumeContext';
import { EXPORT_LABELS } from '@/lib/export-labels';
import {
  Download,
  ChevronDown,
  FileText,
  FileCode,
  FileDown,
  Loader2,
  Check,
  AlertTriangle,
} from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const DownloadDropdown: React.FC = () => {
  const { resumeId, title, content, style, exportContentJson, exportStyleJson } = useResume();
  const [isOpen, setIsOpen] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [downloadingDocx, setDownloadingDocx] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    setIsOpen(false);
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

  const handleDownloadDocx = async () => {
    setDownloadingDocx(true);
    setIsOpen(false);
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
      alert('Failed to export Word document. Please try again.');
    } finally {
      setDownloadingDocx(false);
    }
  };

  const handleDownloadTxt = () => {
    setIsOpen(false);
    let text = `${content.header.name}\n${content.header.title}\n`;
    text += `${content.header.email} | ${content.header.phone} | ${content.header.location}\n`;
    if (content.header.website) text += `${content.header.website}\n`;
    text += `\n${'='.repeat(40)}\n\n`;

    content.sections.forEach((sec) => {
      if (sec.visible === false) return;
      text += `--- ${sec.title.toUpperCase()} ---\n\n`;
      sec.items.forEach((item) => {
        if (item.visible === false) return;
        if (item.title || item.subtitle) {
          text += `${item.title}${item.subtitle ? ' - ' + item.subtitle : ''}${item.dateRange ? ' (' + item.dateRange + ')' : ''}\n`;
        }
        item.bullets?.forEach((b) => {
          text += `  • ${b.text}\n`;
        });
        text += '\n';
      });
    });

    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.toLowerCase().replace(/[^a-z0-9]/g, '_')}_resume.txt`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const handleDownloadFullJson = () => {
    setIsOpen(false);
    const fullResume = {
      id: resumeId,
      title,
      content,
      style,
      exportedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(fullResume, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.toLowerCase().replace(/[^a-z0-9]/g, '_')}_full_resume.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        disabled={downloadingPdf || downloadingDocx}
        className="flex items-center gap-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-all shadow-xs hover:shadow-sm disabled:opacity-50"
      >
        {downloadingPdf || downloadingDocx ? (
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
        ) : (
          <Download className="w-3.5 h-3.5" />
        )}
        <span>Download</span>
        <ChevronDown className="w-3 h-3 ml-0.5 opacity-80" />
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-2xl shadow-2xl border border-slate-200 z-50 p-2 space-y-1 animate-in fade-in zoom-in-95">
          {/* Faithful PDF Download */}
          <button
            type="button"
            onClick={handleDownloadPdf}
            className="w-full p-2.5 rounded-xl hover:bg-blue-50/70 text-left transition-colors group flex items-start gap-3"
          >
            <div className="p-2 bg-rose-50 text-rose-600 rounded-lg group-hover:bg-rose-100 transition-colors mt-0.5">
              <FileDown className="w-4 h-4" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-slate-900 group-hover:text-blue-600">
                  {EXPORT_LABELS.pdf.title}
                </span>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-1.5 py-0.2 rounded">
                  {EXPORT_LABELS.pdf.badge}
                </span>
              </div>
              <p className="text-[11px] text-slate-500 mt-0.5 leading-snug">
                {EXPORT_LABELS.pdf.description}
              </p>
            </div>
          </button>

          {/* Simplified Word Export (.docx) */}
          <button
            type="button"
            onClick={handleDownloadDocx}
            className="w-full p-2.5 rounded-xl hover:bg-slate-50 text-left transition-colors group flex items-start gap-3 border-t border-slate-100"
          >
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg group-hover:bg-blue-100 transition-colors mt-0.5">
              <FileText className="w-4 h-4" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-slate-900 group-hover:text-blue-600">
                  {EXPORT_LABELS.docx.title}
                </span>
                <span className="text-[10px] bg-blue-100 text-blue-800 font-bold px-1.5 py-0.2 rounded">
                  {EXPORT_LABELS.docx.badge}
                </span>
              </div>
              <p className="text-[11px] text-slate-500 mt-0.5 leading-snug">
                {EXPORT_LABELS.docx.description}
              </p>
            </div>
          </button>

          {/* Plain Text (.txt) */}
          <button
            type="button"
            onClick={handleDownloadTxt}
            className="w-full p-2 rounded-xl hover:bg-slate-50 text-left transition-colors group flex items-start gap-3 border-t border-slate-100"
          >
            <div className="p-2 bg-slate-100 text-slate-600 rounded-lg group-hover:bg-slate-200 transition-colors mt-0.5">
              <FileText className="w-4 h-4" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-slate-900">
                  {EXPORT_LABELS.txt.title}
                </span>
              </div>
              <p className="text-[11px] text-slate-500 leading-snug">
                {EXPORT_LABELS.txt.description}
              </p>
            </div>
          </button>

          {/* Full JSON Export */}
          <button
            type="button"
            onClick={handleDownloadFullJson}
            className="w-full p-2 rounded-xl hover:bg-slate-50 text-left transition-colors group flex items-start gap-3 border-t border-slate-100"
          >
            <div className="p-2 bg-purple-50 text-purple-600 rounded-lg group-hover:bg-purple-100 transition-colors mt-0.5">
              <FileCode className="w-4 h-4" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-slate-900">
                  {EXPORT_LABELS.json.title} (v1.1.0)
                </span>
              </div>
              <p className="text-[11px] text-slate-500 leading-snug">
                {EXPORT_LABELS.json.description}
              </p>
            </div>
          </button>
        </div>
      )}
    </div>
  );
};

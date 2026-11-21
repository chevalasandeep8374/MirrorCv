'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useResume } from '@/context/ResumeContext';
import { EXPORT_LABELS } from '@/lib/export-labels';
import { supabase } from '@/lib/supabase';
import {
  Download,
  ChevronDown,
  FileText,
  FileCode,
  FileDown,
  Loader2,
  Check,
  AlertTriangle,
  X,
} from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const DownloadDropdown: React.FC = () => {
  const { resumeId, title, content, style } = useResume();
  const [isOpen, setIsOpen] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [downloadingDocx, setDownloadingDocx] = useState(false);
  const [toastMessage, setToastMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
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

  useEffect(() => {
    if (toastMessage) {
      const timer = setTimeout(() => setToastMessage(null), 6000);
      return () => clearTimeout(timer);
    }
  }, [toastMessage]);

  const getAuthToken = async (): Promise<string> => {
    try {
      const { data } = await supabase.auth.getSession();
      return data?.session?.access_token || '';
    } catch {
      return '';
    }
  };

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    setIsOpen(false);
    setToastMessage(null);

    try {
      const token = await getAuthToken();
      const response = await fetch(`${API_BASE_URL}/api/resumes/${resumeId}/export/pdf`, {
        headers: {
          Authorization: token ? `Bearer ${token}` : '',
        },
      });

      if (!response.ok) {
        let errorDetail = 'PDF generation failed on server.';
        try {
          const errJson = await response.json();
          errorDetail = errJson.detail || errorDetail;
        } catch {
          // non-json error
        }
        throw new Error(errorDetail);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const cleanTitle = (title || 'resume').toLowerCase().replace(/[^a-z0-9]/g, '_');
      a.download = `${cleanTitle}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      setToastMessage({ type: 'success', text: 'PDF exported successfully.' });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'PDF export failed.';
      setToastMessage({ type: 'error', text: msg });
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleDownloadDocx = async () => {
    setDownloadingDocx(true);
    setIsOpen(false);
    setToastMessage(null);

    try {
      const token = await getAuthToken();
      const response = await fetch(`${API_BASE_URL}/api/resumes/${resumeId}/export/docx`, {
        headers: {
          Authorization: token ? `Bearer ${token}` : '',
        },
      });

      if (!response.ok) {
        let errorDetail = 'Word export failed on server.';
        try {
          const errJson = await response.json();
          errorDetail = errJson.detail || errorDetail;
        } catch {
          // non-json error
        }
        throw new Error(errorDetail);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const cleanTitle = (title || 'resume').toLowerCase().replace(/[^a-z0-9]/g, '_');
      a.download = `${cleanTitle}.docx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      setToastMessage({ type: 'success', text: 'Word document exported successfully.' });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to export Word document.';
      setToastMessage({ type: 'error', text: msg });
    } finally {
      setDownloadingDocx(false);
    }
  };

  const handleDownloadTxt = () => {
    setIsOpen(false);
    setToastMessage(null);
    try {
      let text = `${content.header.name || ''}\n${content.header.title || ''}\n`;
      text += `${content.header.email || ''} | ${content.header.phone || ''} | ${content.header.location || ''}\n`;
      if (content.header.website) text += `${content.header.website}\n`;
      text += `\n${'='.repeat(40)}\n\n`;

      content.sections.forEach((sec) => {
        if (sec.visible === false) return;
        text += `--- ${(sec.title || '').toUpperCase()} ---\n\n`;
        sec.items.forEach((item) => {
          if (item.visible === false) return;
          if (item.title || item.subtitle) {
            text += `${item.title || ''}${item.subtitle ? ' - ' + item.subtitle : ''}${item.dateRange ? ' (' + item.dateRange + ')' : ''}\n`;
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
      const cleanTitle = (title || 'resume').toLowerCase().replace(/[^a-z0-9]/g, '_');
      a.download = `${cleanTitle}.txt`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setToastMessage({ type: 'success', text: 'Plain text exported successfully.' });
    } catch {
      setToastMessage({ type: 'error', text: 'Failed to export plain text.' });
    }
  };

  const handleDownloadFullJson = () => {
    setIsOpen(false);
    setToastMessage(null);
    try {
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
      const cleanTitle = (title || 'resume').toLowerCase().replace(/[^a-z0-9]/g, '_');
      a.download = `${cleanTitle}_data.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setToastMessage({ type: 'success', text: 'JSON exported successfully.' });
    } catch {
      setToastMessage({ type: 'error', text: 'Failed to export JSON.' });
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Toast Notification */}
      {toastMessage && (
        <div
          className={`fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 rounded-xl shadow-xl text-xs font-medium border animate-slide-up ${
            toastMessage.type === 'success'
              ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
              : 'bg-rose-50 text-rose-800 border-rose-200'
          }`}
        >
          {toastMessage.type === 'success' ? (
            <Check className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          ) : (
            <AlertTriangle className="w-4 h-4 text-rose-600 flex-shrink-0" />
          )}
          <span>{toastMessage.text}</span>
          <button
            onClick={() => setToastMessage(null)}
            className="ml-2 text-slate-400 hover:text-slate-600"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      <div className="h-9 inline-flex items-center rounded-xl bg-[#181824] hover:bg-black text-white shadow-xs transition-colors duration-150">
        <button
          type="button"
          id="downloadMainBtn"
          onClick={handleDownloadPdf}
          disabled={downloadingPdf || downloadingDocx}
          className="h-full flex items-center gap-2 px-4 text-xs sm:text-sm font-bold text-white cursor-pointer hover:bg-white/10 rounded-l-xl transition-colors"
        >
          {downloadingPdf || downloadingDocx ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Download className="w-4 h-4" />
          )}
          <span>Download</span>
        </button>
        <div className="h-4 border-r border-slate-700" />
        <button
          type="button"
          aria-label="Download formats"
          onClick={() => setIsOpen((prev) => !prev)}
          className="h-full px-2.5 text-slate-300 hover:text-white cursor-pointer rounded-r-xl transition-colors flex items-center justify-center"
        >
          <ChevronDown className="w-4 h-4" />
        </button>
      </div>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 glass-2 rounded-xl shadow-xl border border-slate-200/90 z-50 p-2 space-y-1 animate-dropdown-fade bg-white">
          {/* Faithful PDF Download */}
          <button
            type="button"
            onClick={handleDownloadPdf}
            disabled={downloadingPdf}
            className="w-full p-2.5 rounded-xl hover:bg-blue-50/70 text-left transition-colors group flex items-start gap-3 cursor-pointer"
          >
            <div className="p-2 bg-rose-50 text-rose-600 rounded-lg group-hover:bg-rose-100 transition-colors mt-0.5">
              {downloadingPdf ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileDown className="w-4 h-4" />}
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
              <p className="text-[11px] text-slate-500 mt-0.5 leading-tight">
                {EXPORT_LABELS.pdf.description}
              </p>
            </div>
          </button>

          {/* Editable Word (.docx) */}
          <button
            type="button"
            onClick={handleDownloadDocx}
            disabled={downloadingDocx}
            className="w-full p-2.5 rounded-xl hover:bg-blue-50/70 text-left transition-colors group flex items-start gap-3 cursor-pointer"
          >
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg group-hover:bg-blue-100 transition-colors mt-0.5">
              {downloadingDocx ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
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
              <p className="text-[11px] text-slate-500 mt-0.5 leading-tight">
                {EXPORT_LABELS.docx.description}
              </p>
            </div>
          </button>

          {/* Plain Text (.txt) */}
          <button
            type="button"
            onClick={handleDownloadTxt}
            className="w-full p-2.5 rounded-xl hover:bg-slate-50 text-left transition-colors group flex items-start gap-3 cursor-pointer"
          >
            <div className="p-2 bg-slate-100 text-slate-700 rounded-lg group-hover:bg-slate-200 transition-colors mt-0.5">
              <FileText className="w-4 h-4" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-slate-900">
                  Plain Text (.txt)
                </span>
                <span className="text-[10px] bg-slate-100 text-slate-700 font-bold px-1.5 py-0.2 rounded">
                  ASCII
                </span>
              </div>
              <p className="text-[11px] text-slate-500 mt-0.5 leading-tight">
                Clean text for pasting into application portals
              </p>
            </div>
          </button>

          {/* Full JSON Export */}
          <button
            type="button"
            onClick={handleDownloadFullJson}
            className="w-full p-2.5 rounded-xl hover:bg-amber-50/70 text-left transition-colors group flex items-start gap-3 cursor-pointer"
          >
            <div className="p-2 bg-amber-50 text-amber-600 rounded-lg group-hover:bg-amber-100 transition-colors mt-0.5">
              <FileCode className="w-4 h-4" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-slate-900 group-hover:text-amber-600">
                  Full Resume JSON
                </span>
                <span className="text-[10px] bg-amber-100 text-amber-800 font-bold px-1.5 py-0.2 rounded">
                  Raw Data
                </span>
              </div>
              <p className="text-[11px] text-slate-500 mt-0.5 leading-tight">
                Complete data model including style tokens
              </p>
            </div>
          </button>
        </div>
      )}
    </div>
  );
};

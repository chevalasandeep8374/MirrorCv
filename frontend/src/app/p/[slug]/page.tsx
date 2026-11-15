'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { ResumeContent } from '@/types/content';
import { ResumeStyle } from '@/types/style';
import { ResumeDocument } from '@/components/resume-renderer/ResumeDocument';
import { apiClient } from '@/lib/api';
import {
  FileDown,
  Lock,
  AlertTriangle,
  Sparkles,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';

interface PublicResumeData {
  password_required: boolean;
  is_expired: boolean;
  title?: string;
  content?: ResumeContent;
  style?: ResumeStyle;
  allow_pdf_download: boolean;
  no_index: boolean;
  doc_type: string;
}

export default function PublicResumePage() {
  const params = useParams();
  const slug = params?.slug as string;

  const [data, setData] = useState<PublicResumeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [passwordInput, setPasswordInput] = useState('');
  const [passwordError, setPasswordError] = useState(false);
  const [checkingPassword, setCheckingPassword] = useState(false);

  const fetchPublicResume = async (pw?: string) => {
    try {
      const headers: Record<string, string> = {};
      if (pw) {
        headers['X-Share-Password'] = pw;
      }
      const res = await apiClient.get<PublicResumeData>(`/public/resumes/${slug}`, {
        headers,
      });
      setData(res.data);
      if (pw && res.data.password_required) {
        setPasswordError(true);
      } else {
        setPasswordError(false);
      }
    } catch (err: any) {
      if (err.response?.status === 404) {
        setData(null);
      }
    } finally {
      setLoading(false);
      setCheckingPassword(false);
    }
  };

  useEffect(() => {
    if (slug) {
      fetchPublicResume();
    }
  }, [slug]);

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!passwordInput.trim()) return;
    setCheckingPassword(true);
    fetchPublicResume(passwordInput.trim());
  };

  const handlePrintPdf = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center text-slate-500 font-sans text-sm">
        Loading document...
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl max-w-md w-full p-8 text-center border border-slate-200 shadow-sm">
          <AlertTriangle className="w-10 h-10 text-amber-500 mx-auto mb-3" />
          <h1 className="font-bold text-slate-900 text-lg">Document Not Found</h1>
          <p className="text-xs text-slate-500 mt-2 leading-relaxed">
            This resume link does not exist, has expired, or was disabled by its owner.
          </p>
        </div>
      </div>
    );
  }

  if (data.is_expired) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl max-w-md w-full p-8 text-center border border-slate-200 shadow-sm">
          <AlertTriangle className="w-10 h-10 text-amber-500 mx-auto mb-3" />
          <h1 className="font-bold text-slate-900 text-lg">Link Expired</h1>
          <p className="text-xs text-slate-500 mt-2 leading-relaxed">
            The temporary access window for this document has ended.
          </p>
        </div>
      </div>
    );
  }

  // Password Wall
  if (data.password_required) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl max-w-sm w-full p-6 border border-slate-200 shadow-xl text-center animate-in zoom-in-95">
          <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-3">
            <Lock className="w-6 h-6" />
          </div>
          <h1 className="font-bold text-slate-900 text-base">Protected Resume</h1>
          <p className="text-xs text-slate-500 mt-1">
            The owner has protected this document with a passcode.
          </p>

          <form onSubmit={handlePasswordSubmit} className="mt-5 space-y-3">
            <div>
              <input
                type="password"
                value={passwordInput}
                onChange={(e) => setPasswordInput(e.target.value)}
                placeholder="Enter password..."
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg text-center focus:outline-none focus:ring-1 focus:ring-blue-500"
                autoFocus
              />
              {passwordError && (
                <div className="text-[11px] text-rose-600 font-semibold mt-1">
                  Incorrect password. Please try again.
                </div>
              )}
            </div>

            <button
              type="submit"
              disabled={checkingPassword || !passwordInput.trim()}
              className="w-full py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg text-xs font-bold transition flex items-center justify-center gap-1.5"
            >
              <span>{checkingPassword ? 'Verifying...' : 'View Document'}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col justify-between">
      {/* Top Floating Control Bar */}
      <header className="sticky top-0 z-30 bg-white/90 backdrop-blur-md border-b border-slate-200 print:hidden">
        <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-blue-600" />
            <h1 className="font-bold text-slate-900 text-sm truncate max-w-xs md:max-w-md">
              {data.title || 'Resume'}
            </h1>
          </div>

          {data.allow_pdf_download && (
            <button
              type="button"
              onClick={handlePrintPdf}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg shadow-sm transition"
            >
              <FileDown className="w-3.5 h-3.5" />
              <span>Download PDF</span>
            </button>
          )}
        </div>
      </header>

      {/* Main Document Body */}
      <main className="flex-1 py-8 px-4 flex items-center justify-center print:p-0 print:m-0">
        <div className="shadow-xl rounded-sm print:shadow-none bg-white">
          {data.content && data.style && (
            <ResumeDocument content={data.content} style={data.style} />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="py-6 text-center text-xs text-slate-400 print:hidden border-t border-slate-200 bg-white">
        Powered by{' '}
        <span className="font-bold text-slate-700">MirrorCV</span> — The Exact-Fidelity Resume Engine
      </footer>
    </div>
  );
}

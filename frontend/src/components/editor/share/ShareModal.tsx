'use client';

import React, { useState, useEffect } from 'react';
import { useResume } from '@/context/ResumeContext';
import { apiClient } from '@/lib/api';
import {
  Share2,
  X,
  Copy,
  Check,
  Lock,
  Globe,
  Eye,
  Calendar,
  Download,
  ShieldCheck,
  Clock,
  Sparkles,
} from 'lucide-react';

interface ShareInfo {
  id: string;
  document_id: string;
  slug: string;
  is_active: boolean;
  has_password: boolean;
  expires_at?: string;
  allow_pdf_download: boolean;
  no_index: boolean;
  view_count: number;
  last_viewed_at?: string;
  share_url: string;
}

export const ShareModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({
  isOpen,
  onClose,
}) => {
  const { resumeId } = useResume();
  const [shareInfo, setShareInfo] = useState<ShareInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [saving, setSaving] = useState(false);

  // Form states
  const [isActive, setIsActive] = useState(false);
  const [password, setPassword] = useState('');
  const [allowPdf, setAllowPdf] = useState(true);
  const [noIndex, setNoIndex] = useState(true);

  useEffect(() => {
    if (isOpen) {
      loadShareSettings();
    }
  }, [isOpen, resumeId]);

  const loadShareSettings = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get<ShareInfo>(`/resumes/${resumeId}/share`);
      setShareInfo(res.data);
      setIsActive(res.data.is_active);
      setAllowPdf(res.data.allow_pdf_download);
      setNoIndex(res.data.no_index);
    } catch (err) {
      console.error('Failed to load share settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (activeState?: boolean) => {
    setSaving(true);
    try {
      const targetActive = activeState !== undefined ? activeState : isActive;
      const res = await apiClient.post<ShareInfo>(`/resumes/${resumeId}/share`, {
        is_active: targetActive,
        password: password ? password : password === '' ? '' : undefined,
        allow_pdf_download: allowPdf,
        no_index: noIndex,
      });
      setShareInfo(res.data);
      setIsActive(res.data.is_active);
      setPassword('');
    } catch (err) {
      alert('Failed to update share settings.');
    } finally {
      setSaving(false);
    }
  };

  const getFullPublicUrl = () => {
    if (typeof window === 'undefined' || !shareInfo) return '';
    return `${window.location.origin}/p/${shareInfo.slug}`;
  };

  const handleCopyLink = () => {
    const url = getFullPublicUrl();
    navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95 select-none">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2">
            <Share2 className="w-5 h-5 text-blue-600" />
            <h3 className="font-bold text-slate-900 text-sm">Share Resume Link</h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-800 rounded-lg hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {loading ? (
          <div className="py-12 text-center text-xs text-slate-400">Loading share settings...</div>
        ) : (
          <div className="mt-4 space-y-4">
            {/* Active Toggle */}
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200">
              <div>
                <div className="font-bold text-xs text-slate-900">Public Link Status</div>
                <div className="text-[11px] text-slate-500">
                  {isActive ? 'Anyone with the link can view' : 'Link is currently private and inactive'}
                </div>
              </div>
              <button
                type="button"
                onClick={() => {
                  const next = !isActive;
                  setIsActive(next);
                  handleSave(next);
                }}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  isActive ? 'bg-blue-600' : 'bg-slate-300'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    isActive ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            {/* Share URL Box */}
            {isActive && shareInfo && (
              <div className="space-y-1.5">
                <label className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                  Public URL
                </label>
                <div className="flex items-center space-x-1.5 p-1.5 bg-slate-50 border border-slate-200 rounded-xl">
                  <span className="text-xs font-mono text-slate-600 px-2 truncate flex-1">
                    {getFullPublicUrl()}
                  </span>
                  <button
                    type="button"
                    onClick={handleCopyLink}
                    className="px-3 py-1.5 bg-white border border-slate-300 rounded-lg text-xs font-bold text-slate-800 hover:bg-slate-100 flex items-center gap-1 shrink-0 shadow-2xs"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copied ? 'Copied!' : 'Copy'}</span>
                  </button>
                </div>
              </div>
            )}

            {/* Privacy Controls */}
            <div className="space-y-2.5 pt-2 border-t border-slate-100 text-xs">
              <div>
                <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                  Optional Password Protection
                </label>
                <div className="flex items-center space-x-2">
                  <div className="relative flex-1">
                    <Lock className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder={
                        shareInfo?.has_password ? '•••••••• (Password is set)' : 'Leave empty for no password'
                      }
                      className="w-full pl-8 pr-3 py-1.5 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                  {shareInfo?.has_password && (
                    <button
                      type="button"
                      onClick={() => {
                        setPassword('');
                        handleSave();
                      }}
                      className="text-[11px] text-rose-600 hover:underline font-medium"
                    >
                      Clear
                    </button>
                  )}
                </div>
              </div>

              <div className="flex items-center justify-between pt-1">
                <span className="text-slate-700 font-medium">Allow PDF Download</span>
                <input
                  type="checkbox"
                  checked={allowPdf}
                  onChange={(e) => setAllowPdf(e.target.checked)}
                  className="rounded text-blue-600 w-4 h-4"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <span className="text-slate-700 font-medium">Search Engine No-Index</span>
                  <div className="text-[10px] text-slate-400">Hide from Google and web crawlers</div>
                </div>
                <input
                  type="checkbox"
                  checked={noIndex}
                  onChange={(e) => setNoIndex(e.target.checked)}
                  className="rounded text-blue-600 w-4 h-4"
                />
              </div>
            </div>

            {/* Analytics */}
            {shareInfo && (
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span className="flex items-center gap-1">
                  <Eye className="w-3.5 h-3.5 text-slate-400" />
                  <span>
                    <strong>{shareInfo.view_count}</strong> {shareInfo.view_count === 1 ? 'view' : 'views'}
                  </span>
                </span>

                {shareInfo.last_viewed_at && (
                  <span className="flex items-center gap-1 text-[11px]">
                    <Clock className="w-3 h-3 text-slate-400" />
                    <span>Last viewed {new Date(shareInfo.last_viewed_at).toLocaleDateString()}</span>
                  </span>
                )}
              </div>
            )}

            {/* Save Button */}
            <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-end space-x-2">
              <button
                type="button"
                onClick={onClose}
                className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900"
              >
                Close
              </button>
              <button
                type="button"
                disabled={saving}
                onClick={() => handleSave()}
                className="px-4 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 disabled:opacity-50"
              >
                {saving ? 'Updating...' : 'Save Settings'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

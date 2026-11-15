'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  User,
  X,
  KeyRound,
  Download,
  Trash2,
  CheckCircle2,
  AlertCircle,
  ShieldAlert,
} from 'lucide-react';
import { apiClient } from '@/lib/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface AccountSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AccountSettingsModal: React.FC<AccountSettingsModalProps> = ({
  isOpen,
  onClose,
}) => {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'password' | 'export' | 'danger'>('password');

  // Password change state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [pwLoading, setPwLoading] = useState(false);
  const [pwSuccess, setPwSuccess] = useState<string | null>(null);
  const [pwError, setPwError] = useState<string | null>(null);

  // GDPR export state
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  // Delete account state
  const [deletePassword, setDeletePassword] = useState('');
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setPwError('New passwords do not match.');
      return;
    }
    setPwLoading(true);
    setPwError(null);
    setPwSuccess(null);
    try {
      await apiClient.post('/account/password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      setPwSuccess('Password successfully updated.');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setPwError(axiosErr.response?.data?.detail || 'Failed to update password.');
    } finally {
      setPwLoading(false);
    }
  };

  const handleGdprExport = async () => {
    setExporting(true);
    setExportError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/account/export-data`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('mirrorcv_token') || ''}`,
        },
      });
      if (!response.ok) throw new Error('Export request failed.');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `mirrorcv_gdpr_export_${new Date().toISOString().split('T')[0]}.zip`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      setExportError('Failed to generate GDPR data export. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  const handleDeleteAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!confirm('Are you ABSOLUTELY certain you want to permanently delete your account and all associated resumes, versions, and analytics? This action CANNOT be undone.')) {
      return;
    }
    setDeleteLoading(true);
    setDeleteError(null);
    try {
      await apiClient.post('/account/delete', { password: deletePassword });
      localStorage.removeItem('mirrorcv_token');
      router.push('/login');
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setDeleteError(axiosErr.response?.data?.detail || 'Incorrect password. Account deletion failed.');
      setDeleteLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <User className="w-5 h-5 text-blue-400" />
            <div>
              <h2 className="font-bold text-base leading-tight">Account & Security Settings</h2>
              <p className="text-[11px] text-slate-400">
                Manage credentials, GDPR full data portability, and account lifecycle
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
            onClick={() => setActiveTab('password')}
            className={`py-3 px-4 border-b-2 flex items-center gap-1.5 transition-colors ${
              activeTab === 'password'
                ? 'border-blue-600 text-blue-600 font-bold bg-white'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            <KeyRound className="w-4 h-4" />
            <span>Password</span>
          </button>
          <button
            onClick={() => setActiveTab('export')}
            className={`py-3 px-4 border-b-2 flex items-center gap-1.5 transition-colors ${
              activeTab === 'export'
                ? 'border-blue-600 text-blue-600 font-bold bg-white'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            <Download className="w-4 h-4" />
            <span>GDPR Export</span>
          </button>
          <button
            onClick={() => setActiveTab('danger')}
            className={`py-3 px-4 border-b-2 flex items-center gap-1.5 transition-colors ${
              activeTab === 'danger'
                ? 'border-rose-600 text-rose-600 font-bold bg-white'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            <Trash2 className="w-4 h-4" />
            <span>Danger Zone</span>
          </button>
        </div>

        {/* Tab Body */}
        <div className="p-6 overflow-y-auto space-y-4">
          {/* TAB 1: PASSWORD */}
          {activeTab === 'password' && (
            <form onSubmit={handleChangePassword} className="space-y-3">
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">
                  Current Password
                </label>
                <input
                  type="password"
                  required
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">
                  New Password (min 6 characters)
                </label>
                <input
                  type="password"
                  required
                  minLength={6}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  required
                  minLength={6}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
                />
              </div>

              {pwSuccess && (
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
                  <span>{pwSuccess}</span>
                </div>
              )}

              {pwError && (
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
                  <span>{pwError}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={pwLoading}
                className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition-colors disabled:opacity-50"
              >
                {pwLoading ? 'Updating Password...' : 'Save New Password'}
              </button>
            </form>
          )}

          {/* TAB 2: GDPR FULL DATA EXPORT */}
          {activeTab === 'export' && (
            <div className="space-y-4">
              <p className="text-xs text-slate-600 leading-relaxed">
                Under Article 20 of GDPR (Right to Data Portability), you can download a complete ZIP archive containing all your personal data, including resumes (content and style tokens), version histories, share links, view analytics, and AI usage logs.
              </p>

              {exportError && (
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
                  <span>{exportError}</span>
                </div>
              )}

              <button
                type="button"
                disabled={exporting}
                onClick={handleGdprExport}
                className="w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                <Download className="w-4 h-4" />
                <span>{exporting ? 'Packaging Archive...' : 'Download My Full Data Archive (.zip)'}</span>
              </button>
            </div>
          )}

          {/* TAB 3: DANGER ZONE / ACCOUNT DELETION */}
          {activeTab === 'danger' && (
            <form onSubmit={handleDeleteAccount} className="space-y-4">
              <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl space-y-1.5 text-xs text-rose-800">
                <div className="font-bold flex items-center gap-1.5 text-rose-900">
                  <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0" />
                  <span>Permanent Deletion Warning</span>
                </div>
                <p className="leading-relaxed">
                  Deleting your account permanently removes all stored resumes, tailoring runs, version snapshots, and public share links. This action cannot be reversed.
                </p>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">
                  Confirm Password to Delete Account
                </label>
                <input
                  type="password"
                  required
                  placeholder="Enter your current password"
                  value={deletePassword}
                  onChange={(e) => setDeletePassword(e.target.value)}
                  className="w-full text-xs px-3 py-2 border border-rose-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-rose-500 font-mono"
                />
              </div>

              {deleteError && (
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
                  <span>{deleteError}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={deleteLoading || !deletePassword}
                className="w-full py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-bold transition-colors disabled:opacity-50 flex items-center justify-center gap-1.5"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>{deleteLoading ? 'Deleting Account...' : 'Permanently Delete My Account'}</span>
              </button>
            </form>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="text-xs font-semibold text-slate-600 hover:text-slate-800 px-3 py-1.5"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

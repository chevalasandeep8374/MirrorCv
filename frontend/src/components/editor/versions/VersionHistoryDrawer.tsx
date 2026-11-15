'use client';

import React, { useState, useEffect } from 'react';
import { useResume } from '@/context/ResumeContext';
import { apiClient } from '@/lib/api';
import {
  History,
  X,
  RotateCcw,
  GitCompare,
  BookmarkPlus,
  Clock,
  Sparkles,
  ChevronRight,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';

interface VersionItem {
  id: string;
  document_id: string;
  version_number: number;
  label?: string;
  is_manual: boolean;
  change_summary?: string;
  created_at: string;
}

interface DiffItem {
  path: string;
  type: 'added' | 'removed' | 'modified' | 'unchanged';
  old_value?: string;
  new_value?: string;
}

interface VersionCompareResponse {
  version_a_number: number;
  version_b_number: number;
  diffs: DiffItem[];
}

export const VersionHistoryDrawer: React.FC<{ isOpen: boolean; onClose: () => void }> = ({
  isOpen,
  onClose,
}) => {
  const { resumeId, updateContent, updateStyle } = useResume();
  const [versions, setVersions] = useState<VersionItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [newLabel, setNewLabel] = useState('');
  const [savingVersion, setSavingVersion] = useState(false);
  const [selectedForCompare, setSelectedForCompare] = useState<string[]>([]);
  const [compareResult, setCompareResult] = useState<VersionCompareResponse | null>(null);
  const [comparing, setComparing] = useState(false);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3500);
  };

  const fetchVersions = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get<VersionItem[]>(`/resumes/${resumeId}/versions`);
      setVersions(res.data);
    } catch (err) {
      console.error('Failed to fetch versions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchVersions();
      setCompareResult(null);
      setSelectedForCompare([]);
    }
  }, [isOpen, resumeId]);

  const handleSaveManualVersion = async () => {
    if (!newLabel.trim()) return;
    setSavingVersion(true);
    try {
      await apiClient.post(`/resumes/${resumeId}/versions`, {
        label: newLabel.trim(),
        is_manual: true,
      });
      setNewLabel('');
      showToast('New version saved with label!');
      fetchVersions();
    } catch (err) {
      alert('Failed to save version.');
    } finally {
      setSavingVersion(false);
    }
  };

  const handleRestoreVersion = async (vId: string, vNum: number) => {
    if (
      !confirm(
        `Restore version ${vNum}? This will load version ${vNum} into your editor and record a new restored version in your timeline.`
      )
    )
      return;

    try {
      const res = await apiClient.post<VersionItem>(
        `/resumes/${resumeId}/versions/${vId}/restore`
      );
      // Fetch full restored detail to update active editor state
      const detailRes = await apiClient.get<{ content_snapshot: any; style_snapshot: any }>(
        `/resumes/${resumeId}/versions/${res.data.id}`
      );
      updateContent(detailRes.data.content_snapshot);
      updateStyle(detailRes.data.style_snapshot);

      showToast(`Restored version v${vNum}! Timeline preserved.`);
      fetchVersions();
      onClose();
    } catch (err) {
      alert('Failed to restore version.');
    }
  };

  const toggleSelectForCompare = (vId: string) => {
    setSelectedForCompare((prev) => {
      if (prev.includes(vId)) return prev.filter((id) => id !== vId);
      if (prev.length >= 2) return [prev[1], vId];
      return [...prev, vId];
    });
  };

  const handleRunCompare = async () => {
    if (selectedForCompare.length !== 2) return;
    setComparing(true);
    try {
      const res = await apiClient.post<VersionCompareResponse>(
        `/resumes/${resumeId}/versions/compare`,
        {
          version_a_id: selectedForCompare[0],
          version_b_id: selectedForCompare[1],
        }
      );
      setCompareResult(res.data);
    } catch (err) {
      alert('Failed to compare versions.');
    } finally {
      setComparing(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white shadow-2xl border-l border-slate-200 flex flex-col animate-in slide-in-from-right duration-200 select-none">
      {/* Header */}
      <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
        <div className="flex items-center space-x-2">
          <History className="w-5 h-5 text-blue-600" />
          <h2 className="font-bold text-slate-900 text-sm">Version History</h2>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="p-1 text-slate-400 hover:text-slate-800 rounded-lg hover:bg-slate-200 transition"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Toast Notification */}
      {toastMsg && (
        <div className="m-3 p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{toastMsg}</span>
        </div>
      )}

      {/* Manual Save Input */}
      <div className="p-3.5 border-b border-slate-100 bg-white">
        <label className="block text-[11px] font-bold text-slate-600 uppercase tracking-wider mb-1.5">
          Save Current State
        </label>
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={newLabel}
            onChange={(e) => setNewLabel(e.target.value)}
            placeholder="e.g. Before Stripe interview..."
            className="flex-1 px-3 py-1.5 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
          <button
            type="button"
            disabled={!newLabel.trim() || savingVersion}
            onClick={handleSaveManualVersion}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white rounded-lg text-xs font-bold transition flex items-center gap-1 shrink-0"
          >
            <BookmarkPlus className="w-3.5 h-3.5" />
            <span>Save</span>
          </button>
        </div>
      </div>

      {/* Compare Bar if 2 selected */}
      {selectedForCompare.length === 2 && (
        <div className="p-2.5 bg-blue-50 border-b border-blue-200 flex items-center justify-between text-xs">
          <span className="font-semibold text-blue-800">2 versions selected</span>
          <button
            type="button"
            onClick={handleRunCompare}
            disabled={comparing}
            className="px-3 py-1 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 flex items-center gap-1"
          >
            <GitCompare className="w-3 h-3" />
            <span>{comparing ? 'Comparing...' : 'Compare Side-by-Side'}</span>
          </button>
        </div>
      )}

      {/* Comparison View Result */}
      {compareResult && (
        <div className="p-4 border-b border-slate-200 bg-slate-50 max-h-60 overflow-y-auto">
          <div className="flex items-center justify-between mb-2">
            <span className="font-bold text-xs text-slate-800">
              Diff: v{compareResult.version_a_number} vs v{compareResult.version_b_number}
            </span>
            <button
              type="button"
              onClick={() => setCompareResult(null)}
              className="text-[11px] text-slate-500 hover:underline"
            >
              Close Diff
            </button>
          </div>
          {compareResult.diffs.length === 0 ? (
            <p className="text-xs text-slate-500">No textual changes found between these versions.</p>
          ) : (
            <div className="space-y-2 text-xs">
              {compareResult.diffs.map((d, i) => (
                <div key={i} className="p-2 rounded bg-white border border-slate-200">
                  <div className="font-bold text-[11px] text-slate-700">{d.path}</div>
                  {d.type === 'added' && (
                    <div className="text-emerald-700 bg-emerald-50 p-1 rounded mt-1 font-mono text-[10px]">
                      + {d.new_value}
                    </div>
                  )}
                  {d.type === 'removed' && (
                    <div className="text-rose-700 bg-rose-50 p-1 rounded mt-1 font-mono text-[10px]">
                      - {d.old_value}
                    </div>
                  )}
                  {d.type === 'modified' && (
                    <div className="mt-1 font-mono text-[10px] space-y-0.5">
                      <div className="text-rose-700 bg-rose-50 p-1 rounded">- {d.old_value}</div>
                      <div className="text-emerald-700 bg-emerald-50 p-1 rounded">+ {d.new_value}</div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Version List */}
      <div className="flex-1 p-4 overflow-y-auto space-y-2.5">
        {loading ? (
          <div className="py-8 text-center text-xs text-slate-400">Loading version history...</div>
        ) : versions.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-400">
            No versions saved yet. Auto-snapshots are created during major edits.
          </div>
        ) : (
          versions.map((ver) => {
            const isSelectedForComp = selectedForCompare.includes(ver.id);
            const dateStr = new Date(ver.created_at).toLocaleString();

            return (
              <div
                key={ver.id}
                className={`p-3 rounded-xl border transition-all ${
                  isSelectedForComp
                    ? 'border-blue-500 bg-blue-50/50 shadow-xs'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-xs bg-slate-100 text-slate-800 px-2 py-0.5 rounded">
                      v{ver.version_number}
                    </span>
                    {ver.is_manual ? (
                      <span className="text-[10px] font-bold text-blue-700 bg-blue-100 px-1.5 py-0.2 rounded">
                        Labeled
                      </span>
                    ) : (
                      <span className="text-[10px] text-slate-400 flex items-center gap-0.5">
                        <Clock className="w-3 h-3" />
                        <span>Auto</span>
                      </span>
                    )}
                  </div>

                  <span className="text-[10px] text-slate-400">{dateStr}</span>
                </div>

                <div className="mt-1.5 font-bold text-xs text-slate-900">
                  {ver.label || 'Snapshot'}
                </div>
                {ver.change_summary && (
                  <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-2">
                    {ver.change_summary}
                  </p>
                )}

                <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between">
                  <button
                    type="button"
                    onClick={() => toggleSelectForCompare(ver.id)}
                    className={`text-[11px] font-semibold flex items-center gap-1 ${
                      isSelectedForComp ? 'text-blue-600 font-bold' : 'text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    <GitCompare className="w-3 h-3" />
                    <span>{isSelectedForComp ? 'Selected' : 'Select to Compare'}</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleRestoreVersion(ver.id, ver.version_number)}
                    className="text-[11px] font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1 px-2 py-1 rounded hover:bg-blue-50 transition"
                  >
                    <RotateCcw className="w-3 h-3" />
                    <span>Restore</span>
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

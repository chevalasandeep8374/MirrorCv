'use client';

import React, { useState, useEffect } from 'react';
import { useResume } from '@/context/ResumeContext';
import { BookmarkPlus, Check, Trash2, X, Sparkles } from 'lucide-react';
import { apiClient } from '@/lib/api';

interface UserPresetsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface SavedPreset {
  id: string;
  name: string;
  category: string;
  style: any;
  createdAt: string;
}

export const UserPresetsModal: React.FC<UserPresetsModalProps> = ({ isOpen, onClose }) => {
  const { style, updateStyle } = useResume();
  const [presetName, setPresetName] = useState('');
  const [presetCategory, setPresetCategory] = useState('single');
  const [savedPresets, setSavedPresets] = useState<SavedPreset[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    // Load user's saved presets
    async function loadPresets() {
      setLoading(true);
      try {
        const res = await apiClient.get<SavedPreset[]>('/api/presets');
        if (Array.isArray(res.data)) {
          setSavedPresets(res.data);
        }
      } catch (err) {
        // Fallback to localStorage if API route is not running in offline mode
        const local = localStorage.getItem('mirrorcv_user_presets');
        if (local) {
          try {
            setSavedPresets(JSON.parse(local));
          } catch (e) {}
        }
      } finally {
        setLoading(false);
      }
    }
    loadPresets();
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSaveCurrentStyle = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!presetName.trim()) return;

    setSaving(true);
    setStatusMsg(null);

    const newPreset: SavedPreset = {
      id: `preset_${Date.now()}`,
      name: presetName.trim(),
      category: presetCategory,
      style: JSON.parse(JSON.stringify(style)),
      createdAt: new Date().toISOString(),
    };

    try {
      await apiClient.post('/api/presets', newPreset);
      setSavedPresets((prev) => [newPreset, ...prev]);
      setStatusMsg('Preset saved successfully!');
      setPresetName('');
    } catch (err) {
      // Local fallback
      const updated = [newPreset, ...savedPresets];
      localStorage.setItem('mirrorcv_user_presets', JSON.stringify(updated));
      setSavedPresets(updated);
      setStatusMsg('Saved locally to this device!');
      setPresetName('');
    } finally {
      setSaving(false);
      setTimeout(() => setStatusMsg(null), 3000);
    }
  };

  const handleApplyPreset = (preset: SavedPreset) => {
    updateStyle(preset.style);
    onClose();
  };

  const handleDeletePreset = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await apiClient.delete(`/api/presets/${id}`);
    } catch (err) {}
    const updated = savedPresets.filter((p) => p.id !== id);
    setSavedPresets(updated);
    localStorage.setItem('mirrorcv_user_presets', JSON.stringify(updated));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-3xl max-w-lg w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
              <BookmarkPlus className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-slate-900">My Saved Templates</h3>
              <p className="text-xs text-slate-500">Save current design tokens or load a saved preset</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Form: Save Current */}
          <form onSubmit={handleSaveCurrentStyle} className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-3">
            <label className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-indigo-600" /> Save Current Design as Preset
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="e.g. Modern Tech Minimalist"
                value={presetName}
                onChange={(e) => setPresetName(e.target.value)}
                required
                className="flex-1 text-xs px-3 py-2 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-hidden"
              />
              <button
                type="submit"
                disabled={saving || !presetName.trim()}
                className="px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-xl transition-colors shadow-xs"
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
            </div>
            {statusMsg && (
              <div className="text-[11px] font-semibold text-emerald-600 animate-in fade-in">
                {statusMsg}
              </div>
            )}
          </form>

          {/* List of Saved Presets */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-700">Your Custom Presets</label>
            {loading ? (
              <div className="text-xs text-slate-400 text-center py-6">Loading presets...</div>
            ) : savedPresets.length === 0 ? (
              <div className="text-xs text-slate-400 text-center py-6 border border-dashed border-slate-200 rounded-2xl">
                No custom templates saved yet. Save your favorite styling above!
              </div>
            ) : (
              <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                {savedPresets.map((preset) => (
                  <div
                    key={preset.id}
                    onClick={() => handleApplyPreset(preset)}
                    className="p-3 bg-white rounded-xl border border-slate-200 hover:border-indigo-400 hover:shadow-xs cursor-pointer flex items-center justify-between transition-all group"
                  >
                    <div>
                      <div className="text-xs font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
                        {preset.name}
                      </div>
                      <div className="text-[10px] text-slate-400">
                        {new Date(preset.createdAt).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <button
                        type="button"
                        onClick={(e) => handleDeletePreset(preset.id, e)}
                        className="text-slate-300 hover:text-red-500 p-1.5 rounded-lg hover:bg-red-50 transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end px-6 py-3 bg-slate-50 border-t border-slate-100">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-200/70 rounded-xl transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

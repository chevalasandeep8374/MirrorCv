'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Layers,
  Plus,
  Trash2,
  ArrowLeft,
  CheckCircle2,
  Sparkles,
  Loader2,
  FileText,
  AlertCircle,
} from 'lucide-react';
import { apiClient } from '@/lib/api';

interface MasterProfileItem {
  id: string;
  type: string;
  text: string;
  metadata: Record<string, any>;
  created_at?: string;
}

export default function MasterProfilePage() {
  const [items, setItems] = useState<MasterProfileItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // New item form
  const [newItemType, setNewItemType] = useState('skill');
  const [newItemText, setNewItemText] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchItems = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/master-profile/items');
      setItems(res.data);
      setError(null);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to fetch master profile items.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const handleAddItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItemText.trim()) return;

    setSubmitting(true);
    try {
      const res = await apiClient.post('/master-profile/items', {
        type: newItemType,
        text: newItemText.trim(),
        confirmed: true,
        metadata: { source: 'user_manual_entry' },
      });
      setItems([res.data, ...items]);
      setNewItemText('');
    } catch (err: any) {
      alert('Failed to add item: ' + (err?.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteItem = async (itemId: string) => {
    if (!confirm('Are you sure you want to delete this master profile item?')) return;
    try {
      await apiClient.delete(`/master-profile/items/${itemId}`);
      setItems(items.filter((item) => item.id !== itemId));
    } catch (err: any) {
      alert('Failed to delete item: ' + (err?.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Navigation */}
      <header className="h-16 border-b border-slate-200 bg-white px-6 flex items-center justify-between shadow-sm">
        <div className="flex items-center space-x-3">
          <Link
            href="/"
            className="w-9 h-9 rounded-xl border border-slate-200 flex items-center justify-center text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-purple-600 text-white flex items-center justify-center">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-slate-900 leading-tight">Master Profile Repository</h1>
              <p className="text-[11px] text-slate-500">Verified accomplishments & confirmed skills for AI tailoring</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-8 space-y-8">
        {/* Intro Banner */}
        <div className="p-6 rounded-2xl bg-gradient-to-r from-purple-900 to-indigo-900 text-white shadow-lg">
          <div className="flex items-start justify-between gap-4">
            <div>
              <span className="text-[10px] font-bold tracking-wider text-purple-300 uppercase">
                Single Source of Truth
              </span>
              <h2 className="text-xl font-bold mt-1">Your Verified Career Assets</h2>
              <p className="text-xs text-purple-200 mt-1 max-w-2xl leading-relaxed">
                Agent 2 uses your Master Profile to fill skill gaps and recommend grounded bullet variations.
                Any skill or project you confirm here is permanently authorized for target job descriptions.
              </p>
            </div>
            <div className="hidden sm:flex px-4 py-2 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 text-center">
              <div>
                <span className="text-2xl font-black text-white">{items.length}</span>
                <span className="block text-[10px] text-purple-200 uppercase font-semibold">Verified Items</span>
              </div>
            </div>
          </div>
        </div>

        {/* Add Item Card */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center space-x-2">
            <Plus className="w-4 h-4 text-purple-600" />
            <span>Add Verified Experience or Skill</span>
          </h3>

          <form onSubmit={handleAddItem} className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-3">
              <select
                value={newItemType}
                onChange={(e) => setNewItemType(e.target.value)}
                className="px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs font-semibold text-slate-700 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-purple-500 outline-none"
              >
                <option value="skill">Technical Skill</option>
                <option value="project">Project / Accomplishment</option>
                <option value="achievement">Key Achievement</option>
                <option value="certification">Certification</option>
              </select>

              <input
                type="text"
                value={newItemText}
                onChange={(e) => setNewItemText(e.target.value)}
                placeholder="e.g. Kubernetes cluster deployment with Helm or Automated GraphQL schema migrations"
                className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all"
              />

              <button
                type="submit"
                disabled={submitting || !newItemText.trim()}
                className="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold shadow-sm disabled:opacity-50 flex items-center justify-center space-x-1.5 transition-all"
              >
                {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                <span>Add Item</span>
              </button>
            </div>
          </form>
        </div>

        {/* List of Items */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              Confirmed Master Items ({items.length})
            </h3>
          </div>

          {loading ? (
            <div className="py-12 flex items-center justify-center text-slate-400 space-x-2">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span className="text-xs font-semibold">Loading items...</span>
            </div>
          ) : items.length === 0 ? (
            <div className="p-8 rounded-2xl bg-white border border-dashed border-slate-300 text-center text-slate-500">
              <FileText className="w-8 h-8 mx-auto text-slate-400 mb-2" />
              <p className="text-sm font-semibold text-slate-700">No master profile items yet</p>
              <p className="text-xs text-slate-500 mt-1">
                Add skills or projects above, or confirm skills recommended in the Tailor modal.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-2.5">
              {items.map((item) => (
                <div
                  key={item.id}
                  className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm flex items-center justify-between gap-4 hover:border-slate-300 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <span className="px-2.5 py-1 rounded-lg bg-purple-50 border border-purple-200 text-purple-700 text-[10px] font-bold uppercase tracking-wider shrink-0">
                      {item.type}
                    </span>
                    <span className="text-xs font-medium text-slate-900">{item.text}</span>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleDeleteItem(item.id)}
                    className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors shrink-0"
                    title="Delete item"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

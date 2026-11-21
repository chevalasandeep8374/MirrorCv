'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { TEMPLATE_PRESETS } from '@/lib/presets';
import { ResumeStyle } from '@/types/style';
import { TemplateCard } from '@/components/templates/TemplateCard';
import { apiClient } from '@/lib/api';
import { ArrowLeft, Sparkles, Plus, Layers, Filter } from 'lucide-react';
import Link from 'next/link';

import { getActiveRepository } from '@/repositories';

interface UserPresetItem {
  id: string;
  name: string;
  description?: string;
  category?: string;
  style: ResumeStyle;
}

export default function TemplateGalleryPage() {
  const router = useRouter();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [userPresets, setUserPresets] = useState<UserPresetItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);

  // Load custom presets from backend
  useEffect(() => {
    async function loadUserPresets() {
      try {
        const res = await apiClient.get<UserPresetItem[]>('/templates/user-presets');
        setUserPresets(res.data);
      } catch (err) {
        console.warn('Could not load user presets (user might be unauthenticated):', err);
      }
    }
    loadUserPresets();
  }, []);

  const handleDeleteUserPreset = async (presetId: string) => {
    try {
      await apiClient.delete(`/templates/user-presets/${presetId}`);
      setUserPresets((prev) => prev.filter((p) => p.id !== presetId));
    } catch (err) {
      alert('Failed to delete preset.');
    }
  };

  const handleSelectTemplate = async (style: ResumeStyle) => {
    if (creating) return;
    setCreating(true);
    try {
      const repo = await getActiveRepository();
      const newResume = await repo.create({
        title: `Resume – ${style.templateId || 'Template'}`,
        style,
      });
      router.push(`/editor/${newResume.id}`);
    } catch (err) {
      console.error('Failed to create resume from template:', err);
      alert('Failed to initialize resume. Please log in or try again.');
      setCreating(false);
    }
  };

  const categories = [
    { id: 'all', label: 'All Templates' },
    { id: 'single', label: 'Single Column' },
    { id: 'sidebar', label: 'Two-Column Sidebar' },
    { id: 'banner', label: 'Header Banner' },
    { id: 'compact', label: 'Compact Technical' },
    { id: 'creative', label: 'Creative & Accent' },
    { id: 'academic', label: 'Academic CV' },
    { id: 'user', label: `My Presets (${userPresets.length})` },
  ];

  const allTemplates = [
    ...TEMPLATE_PRESETS.map((p) => ({
      id: p.id,
      name: p.name,
      category: p.category,
      description: p.description,
      style: p.style,
      isUserPreset: false,
    })),
    ...userPresets.map((up) => ({
      id: up.id,
      name: up.name,
      category: up.category || 'custom',
      description: up.description || 'Custom saved style preset.',
      style: up.style,
      isUserPreset: true,
    })),
  ];

  const filteredTemplates = allTemplates.filter((tpl) => {
    if (selectedCategory === 'all') return true;
    if (selectedCategory === 'user') return tpl.isUserPreset;
    return tpl.category === selectedCategory;
  });

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Header */}
      <header className="sticky top-0 z-30 bg-white/90 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link
              href="/"
              className="inline-flex items-center text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors"
            >
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              <span>Back to Dashboard</span>
            </Link>
            <div className="h-4 w-px bg-slate-200" />
            <div className="flex items-center space-x-2">
              <Layers className="w-5 h-5 text-blue-600" />
              <h1 className="text-lg font-bold text-slate-900 tracking-tight">
                Template Gallery
              </h1>
            </div>
          </div>

          <div className="text-xs text-slate-500 font-medium">
            8 FlowCV-Grade Presets · Infinite Token Customization
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-6 py-8 flex-1 w-full">
        <div className="mb-8">
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">
            Choose a Template Preset
          </h2>
          <p className="text-sm text-slate-500 mt-1 max-w-2xl">
            Every template separates content from presentation. You can switch templates anytime
            without losing content or formatting.
          </p>
        </div>

        {/* Category Pills */}
        <div className="flex flex-wrap items-center gap-2 mb-8 border-b border-slate-200 pb-4">
          <Filter className="w-4 h-4 text-slate-400 mr-1" />
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                selectedCategory === cat.id
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Template Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredTemplates.map((tpl) => (
            <TemplateCard
              key={tpl.id}
              id={tpl.id}
              name={tpl.name}
              category={tpl.category}
              description={tpl.description}
              style={tpl.style}
              isUserPreset={tpl.isUserPreset}
              onSelect={handleSelectTemplate}
              onDelete={handleDeleteUserPreset}
            />
          ))}
        </div>
      </main>
    </div>
  );
}

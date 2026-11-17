'use client';

import React, { useState } from 'react';
import { useResume } from '@/context/ResumeContext';
import { TEMPLATE_PRESETS } from '@/lib/presets';
import { Check, LayoutTemplate, X, Sparkles } from 'lucide-react';
import Image from 'next/image';

interface TemplateGalleryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const TemplateGalleryModal: React.FC<TemplateGalleryModalProps> = ({
  isOpen,
  onClose,
}) => {
  const { style, applyPreset } = useResume();
  const [activeCategory, setActiveCategory] = useState<'all' | 'single' | 'sidebar' | 'creative'>('all');
  const [pendingPreset, setPendingPreset] = useState<{ id: string; name: string; style: any } | null>(null);

  if (!isOpen) return null;

  const currentTemplateId = style.templateId;

  const filteredPresets = TEMPLATE_PRESETS.filter((p) => {
    if (activeCategory === 'all') return true;
    if (activeCategory === 'single') return p.style.layout.type === 'single';
    if (activeCategory === 'sidebar')
      return p.style.layout.type === 'sidebar_left' || p.style.layout.type === 'sidebar_right';
    if (activeCategory === 'creative')
      return (
        p.style.layout.type === 'header_banner' ||
        p.style.layout.type === 'creative' ||
        p.style.layout.type === 'academic'
      );
    return true;
  });

  const handleSelectPreset = (presetId: string) => {
    const matched = TEMPLATE_PRESETS.find((p) => p.id === presetId);
    if (!matched) return;
    setPendingPreset({ id: matched.id, name: matched.name, style: matched.style });
  };

  const handleConfirmApply = () => {
    if (!pendingPreset) return;
    // Apply tokens only with undo support, preserving content
    applyPreset({
      ...pendingPreset.style,
      pageSize: style.pageSize, // Retain user's current pageSize preference
      locale: style.locale,     // Retain user's current locale
      direction: style.direction,
    });
    setPendingPreset(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-3xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-blue-50 text-blue-600 rounded-xl">
              <LayoutTemplate className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-slate-900">Design Template Gallery</h3>
              <p className="text-xs text-slate-500">
                Choose a handcrafted design preset. Applying sets style tokens without modifying your content.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Categories Bar */}
        <div className="flex items-center gap-2 px-6 py-3 bg-slate-50 border-b border-slate-100 overflow-x-auto">
          {[
            { id: 'all', label: 'All Templates (8)' },
            { id: 'single', label: 'Single Column' },
            { id: 'sidebar', label: 'Two Columns' },
            { id: 'creative', label: 'Creative & Academic' },
          ].map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id as any)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-colors ${
                activeCategory === cat.id
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Gallery Grid */}
        <div className="p-6 overflow-y-auto flex-1 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {filteredPresets.map((preset) => {
            const isSelected = currentTemplateId === preset.id;
            return (
              <div
                key={preset.id}
                onClick={() => handleSelectPreset(preset.id)}
                className={`group cursor-pointer rounded-2xl border-2 p-2.5 flex flex-col transition-all bg-white hover:shadow-md ${
                  isSelected
                    ? 'border-blue-600 ring-2 ring-blue-600/20 shadow-xs'
                    : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                {/* Thumbnail Preview */}
                <div className="relative aspect-1/1.414 w-full bg-slate-100 rounded-xl overflow-hidden border border-slate-100 flex items-center justify-center">
                  <Image
                    src={`/templates/thumbnails/${preset.id}.webp`}
                    alt={preset.name}
                    width={350}
                    height={495}
                    loading="lazy"
                    className="w-full h-full object-cover object-top transition-transform duration-200 group-hover:scale-102"
                  />
                  {isSelected && (
                    <div className="absolute top-2 right-2 bg-blue-600 text-white p-1 rounded-full shadow-md">
                      <Check className="w-3.5 h-3.5" />
                    </div>
                  )}
                </div>

                {/* Info */}
                <div className="mt-2.5 flex items-center justify-between">
                  <div>
                    <h4 className="text-xs font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                      {preset.name}
                    </h4>
                    <p className="text-[10px] text-slate-500 capitalize">{preset.category} Layout</p>
                  </div>
                  {isSelected && (
                    <span className="text-[9px] font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded">
                      Active
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-3 bg-slate-50 border-t border-slate-100 text-xs text-slate-500">
          <div className="flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
            <span>Pre-rendered vector templates with instantaneous token application.</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 font-semibold text-slate-700 hover:bg-slate-200/70 rounded-xl transition-colors"
          >
            Close
          </button>
        </div>
      </div>

      {/* Template Apply Confirmation Dialog */}
      {pendingPreset && (
        <div className="fixed inset-0 z-60 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl border border-slate-200 space-y-4 animate-in fade-in zoom-in-95">
            <h4 className="font-bold text-base text-slate-900">Apply Template &quot;{pendingPreset.name}&quot;?</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Applying this design preset will update your layout and styling tokens while keeping your resume content intact. You can restore your previous styling anytime by pressing <strong>Ctrl+Z</strong> (Undo).
            </p>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setPendingPreset(null)}
                className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmApply}
                className="px-4 py-1.5 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition-colors"
              >
                Apply Template
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

'use client';

import React, { useState } from 'react';
import { useResume } from '@/context/ResumeContext';
import { Lock, Unlock, LayoutTemplate, BookmarkPlus, Sparkles } from 'lucide-react';
import { DocumentSettingsCard } from './DocumentSettingsCard';
import { LayoutCard } from './LayoutCard';
import { TypographyCard } from './TypographyCard';
import { FontPickerCard } from './FontPickerCard';
import { SpacingMarginsCard } from './SpacingMarginsCard';
import { EntryLayoutCard } from './EntryLayoutCard';
import { SectionHeadingsCard } from './SectionHeadingsCard';
import { ColorsCard } from './ColorsCard';
import { HeaderPhotoCard } from './HeaderPhotoCard';
import { SectionCustomizersCard } from './SectionCustomizersCard';
import { TemplateGalleryModal } from './TemplateGalleryModal';
import { DetachTemplateModal } from './DetachTemplateModal';
import { UserPresetsModal } from './UserPresetsModal';

export const CustomizeTab: React.FC = () => {
  const { style, updateStyle, setTitle, title } = useResume();
  const [galleryOpen, setGalleryOpen] = useState(false);
  const [detachModalOpen, setDetachModalOpen] = useState(false);
  const [userPresetsOpen, setUserPresetsOpen] = useState(false);

  // DOCX Lock verification
  const isLocked = Boolean(
    style.isLocked ||
    (typeof style.templateId === 'string' && style.templateId.startsWith('uploaded:'))
  );

  const handleConfirmDetach = () => {
    updateStyle({
      ...style,
      templateId: 'custom-from-upload',
      isLocked: false,
    });
    setTitle(`${title} (Custom Design)`);
  };

  return (
    <div className="space-y-6 pb-12">
      {/* 1. DOCX Template Hard Lock Banner */}
      {isLocked && (
        <div className="bg-amber-500/10 border-2 border-amber-500/40 rounded-2xl p-4 shadow-sm animate-in fade-in">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-amber-500 text-white rounded-xl shadow-xs mt-0.5">
                <Lock className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-amber-950">
                  Layout & typography are locked to your uploaded Word (.docx) template
                </h4>
                <p className="text-xs text-amber-900/80 mt-1 leading-relaxed max-w-lg">
                  To protect byte-fidelity composition and avoid displacing template slots, fine-grained styling sliders are restricted. You can detach into an editor-native layout to customize all design tokens freely.
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setDetachModalOpen(true)}
              className="px-4 py-2 text-xs font-bold text-amber-950 bg-amber-400 hover:bg-amber-300 rounded-xl shadow-xs transition-colors shrink-0 flex items-center gap-1.5"
            >
              <Unlock className="w-3.5 h-3.5" />
              Detach to edit design
            </button>
          </div>
        </div>
      )}

      {/* 2. Quick Action Toolbar: Templates & User Presets */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={() => setGalleryOpen(true)}
          disabled={isLocked}
          className="flex-1 py-3 px-4 bg-white border border-slate-200 hover:border-blue-400 rounded-2xl shadow-xs flex items-center justify-center gap-2 text-xs font-bold text-slate-800 transition-all hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed group"
        >
          <LayoutTemplate className="w-4 h-4 text-blue-600 group-hover:scale-110 transition-transform" />
          <span>Browse Templates (8 presets)</span>
        </button>

        <button
          type="button"
          onClick={() => setUserPresetsOpen(true)}
          disabled={isLocked}
          className="py-3 px-4 bg-white border border-slate-200 hover:border-indigo-400 rounded-2xl shadow-xs flex items-center justify-center gap-2 text-xs font-bold text-slate-800 transition-all hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed group"
        >
          <BookmarkPlus className="w-4 h-4 text-indigo-600 group-hover:scale-110 transition-transform" />
          <span>My Presets</span>
        </button>
      </div>

      {/* 3. Grouped Customization Cards */}
      <div className={`space-y-5 transition-opacity ${isLocked ? 'opacity-60 pointer-events-none' : ''}`}>
        {/* Document Settings (Language, Date Format, Page Format) */}
        <DocumentSettingsCard />

        {/* Layout & Columns */}
        <LayoutCard />

        {/* Typography & Baseline Offsets */}
        <TypographyCard />

        {/* Curated Self-Hosted Fonts */}
        <FontPickerCard />

        {/* Spacing & Margins (mm & pt) */}
        <SpacingMarginsCard />

        {/* Entry Header Layout */}
        <EntryLayoutCard />

        {/* Section Headings */}
        <SectionHeadingsCard />

        {/* Colors & Granular Accent Toggles */}
        <ColorsCard />

        {/* Header & Photo Framing */}
        <HeaderPhotoCard />

        {/* Section-Specific Customizers */}
        <SectionCustomizersCard />
      </div>

      {/* Modals */}
      <TemplateGalleryModal
        isOpen={galleryOpen}
        onClose={() => setGalleryOpen(false)}
      />

      <DetachTemplateModal
        isOpen={detachModalOpen}
        onClose={() => setDetachModalOpen(false)}
        onConfirmDetach={handleConfirmDetach}
      />

      <UserPresetsModal
        isOpen={userPresetsOpen}
        onClose={() => setUserPresetsOpen(false)}
      />
    </div>
  );
};

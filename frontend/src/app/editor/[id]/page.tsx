'use client';

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import { ResumeProvider, useResume } from '@/context/ResumeContext';
import { EditorHeader } from '@/components/editor/EditorHeader';
import { LeftPanel } from '@/components/editor/LeftPanel';
import { LivePreviewPane } from '@/components/editor/preview/LivePreviewPane';
import { VersionHistoryDrawer } from '@/components/editor/versions/VersionHistoryDrawer';
import { ShareModal } from '@/components/editor/share/ShareModal';
import { AiAssistantModal } from '@/components/editor/ai/AiAssistantModal';
import { AtsModal } from '@/components/editor/ats/AtsModal';
import { TailorModal } from '@/components/editor/tailor/TailorModal';
import { FileText, Sliders, Eye } from 'lucide-react';

function EditorLayout() {
  const { resumeId, title, activeTab, setActiveTab } = useResume();
  const [mobileTab, setMobileTab] = useState<'edit' | 'style' | 'preview'>('edit');
  const [versionsOpen, setVersionsOpen] = useState(false);
  const [shareOpen, setShareOpen] = useState(false);
  const [aiOpen, setAiOpen] = useState(false);
  const [atsOpen, setAtsOpen] = useState(false);
  const [tailorOpen, setTailorOpen] = useState(false);

  const handleMobileTabSwitch = (tab: 'edit' | 'style' | 'preview') => {
    setMobileTab(tab);
    if (tab === 'edit') setActiveTab('content');
    if (tab === 'style') setActiveTab('style');
  };

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-slate-100">
      {/* Top App Header */}
      <EditorHeader
        onOpenVersions={() => setVersionsOpen(true)}
        onOpenShare={() => setShareOpen(true)}
        onOpenAi={() => setAiOpen(true)}
        onOpenAts={() => setAtsOpen(true)}
        onOpenTailor={() => setTailorOpen(true)}
      />

      {/* Split Viewport (Desktop) & Tabbed Viewport (Mobile) */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Edit Controls (Content & Style) */}
        <div
          className={`h-full ${
            mobileTab === 'preview' ? 'hidden md:flex' : 'flex'
          } w-full md:w-[480px] lg:w-[500px] shrink-0`}
        >
          <LeftPanel />
        </div>

        {/* Right Live Document Preview */}
        <div
          className={`flex-1 h-full ${
            mobileTab !== 'preview' ? 'hidden md:flex' : 'flex'
          }`}
        >
          <LivePreviewPane />
        </div>
      </div>

      {/* Modals & Drawers */}
      <VersionHistoryDrawer
        isOpen={versionsOpen}
        onClose={() => setVersionsOpen(false)}
      />
      <ShareModal isOpen={shareOpen} onClose={() => setShareOpen(false)} />
      <AiAssistantModal isOpen={aiOpen} onClose={() => setAiOpen(false)} />
      <AtsModal isOpen={atsOpen} onClose={() => setAtsOpen(false)} />
      <TailorModal
        isOpen={tailorOpen}
        onClose={() => setTailorOpen(false)}
        resumeId={resumeId}
        resumeTitle={title}
      />

      {/* Mobile Responsive Bottom Navigation Bar */}
      <div className="md:hidden h-14 bg-white border-t border-slate-200 flex items-center justify-around px-4 z-40">
        <button
          type="button"
          onClick={() => handleMobileTabSwitch('edit')}
          className={`flex flex-col items-center justify-center space-y-1 text-xs font-semibold py-1 px-3 rounded-lg transition-colors ${
            mobileTab === 'edit'
              ? 'text-blue-600 bg-blue-50'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Edit</span>
        </button>

        <button
          type="button"
          onClick={() => handleMobileTabSwitch('style')}
          className={`flex flex-col items-center justify-center space-y-1 text-xs font-semibold py-1 px-3 rounded-lg transition-colors ${
            mobileTab === 'style'
              ? 'text-blue-600 bg-blue-50'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <Sliders className="w-4 h-4" />
          <span>Style</span>
        </button>

        <button
          type="button"
          onClick={() => handleMobileTabSwitch('preview')}
          className={`flex flex-col items-center justify-center space-y-1 text-xs font-semibold py-1 px-3 rounded-lg transition-colors ${
            mobileTab === 'preview'
              ? 'text-blue-600 bg-blue-50'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <Eye className="w-4 h-4" />
          <span>Preview</span>
        </button>
      </div>
    </div>
  );
}

export default function EditorPage() {
  const params = useParams();
  const id = params?.id as string;

  if (!id) {
    return (
      <div className="flex h-screen items-center justify-center text-slate-500 font-sans">
        Loading editor...
      </div>
    );
  }

  return (
    <ResumeProvider resumeId={id}>
      <EditorLayout />
    </ResumeProvider>
  );
}

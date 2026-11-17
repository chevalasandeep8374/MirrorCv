'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { ResumeProvider, useResume } from '@/context/ResumeContext';
import { EditorHeader } from '@/components/editor/EditorHeader';
import { LeftPanel } from '@/components/editor/LeftPanel';
import { LivePreviewPane } from '@/components/editor/preview/LivePreviewPane';
import { OverviewTab } from '@/components/editor/overview/OverviewTab';
import { AiToolsTab } from '@/components/editor/ai/AiToolsTab';
import { VersionHistoryDrawer } from '@/components/editor/versions/VersionHistoryDrawer';
import { ShareModal } from '@/components/editor/share/ShareModal';
import { AiAssistantModal } from '@/components/editor/ai/AiAssistantModal';
import { AtsModal } from '@/components/editor/ats/AtsModal';
import { TailorModal } from '@/components/editor/tailor/TailorModal';
import { FileText, Sliders, Eye, TrendingUp, Sparkles } from 'lucide-react';

function EditorLayout() {
  const {
    resumeId,
    title,
    activeTab,
    setActiveTab,
    undo,
    redo,
    saveNow,
  } = useResume();

  const [mobileTab, setMobileTab] = useState<'overview' | 'content' | 'customize' | 'ai' | 'preview'>('content');
  const [versionsOpen, setVersionsOpen] = useState(false);
  const [shareOpen, setShareOpen] = useState(false);
  const [aiOpen, setAiOpen] = useState(false);
  const [atsOpen, setAtsOpen] = useState(false);
  const [tailorOpen, setTailorOpen] = useState(false);

  // Global Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isCmdOrCtrl = e.metaKey || e.ctrlKey;
      if (!isCmdOrCtrl) return;

      if (e.key === 's' || e.key === 'S') {
        e.preventDefault();
        saveNow();
      } else if (e.key === 'z' || e.key === 'Z') {
        if (e.shiftKey) {
          e.preventDefault();
          redo();
        } else {
          e.preventDefault();
          undo();
        }
      } else if (e.key === 'y' || e.key === 'Y') {
        e.preventDefault();
        redo();
      } else if (e.key === '1') {
        e.preventDefault();
        setActiveTab('overview');
      } else if (e.key === '2') {
        e.preventDefault();
        setActiveTab('content');
      } else if (e.key === '3') {
        e.preventDefault();
        setActiveTab('customize');
      } else if (e.key === '4') {
        e.preventDefault();
        setActiveTab('ai');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [saveNow, undo, redo, setActiveTab]);

  const handleMobileTabSwitch = (tab: 'overview' | 'content' | 'customize' | 'ai' | 'preview') => {
    setMobileTab(tab);
    if (tab !== 'preview') {
      setActiveTab(tab);
    }
  };

  const isSplitPaneMode =
    activeTab === 'content' || activeTab === 'customize' || activeTab === 'style';

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

      {/* Main View Area */}
      <main className="flex-1 flex overflow-hidden relative">
        {activeTab === 'overview' ? (
          /* Full Overview Dashboard Tab */
          <div className="flex-1 overflow-y-auto bg-slate-100">
            <OverviewTab
              onOpenAts={() => setAtsOpen(true)}
              onOpenTailor={() => setTailorOpen(true)}
              onOpenVersions={() => setVersionsOpen(true)}
              onOpenShare={() => setShareOpen(true)}
            />
          </div>
        ) : activeTab === 'ai' ? (
          /* Full AI Tools Tab */
          <div className="flex-1 overflow-y-auto bg-slate-100">
            <AiToolsTab
              onOpenTailorModal={() => setTailorOpen(true)}
              onOpenAtsModal={() => setAtsOpen(true)}
            />
          </div>
        ) : (
          /* Split Viewport (Desktop) & Tabbed Viewport (Mobile) for Content & Customize */
          <>
            <div
              className={`h-full ${
                mobileTab === 'preview' ? 'hidden md:flex' : 'flex'
              } w-full md:w-[480px] lg:w-[500px] shrink-0`}
            >
              <LeftPanel />
            </div>

            <div
              className={`flex-1 h-full ${
                mobileTab !== 'preview' ? 'hidden md:flex' : 'flex'
              }`}
            >
              <LivePreviewPane />
            </div>
          </>
        )}
      </main>

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
      <div className="md:hidden h-14 bg-white border-t border-slate-200 flex items-center justify-around px-3 z-40">
        <button
          type="button"
          onClick={() => handleMobileTabSwitch('overview')}
          className={`flex flex-col items-center justify-center space-y-1 text-[11px] font-semibold py-1 px-2.5 rounded-lg transition-colors ${
            activeTab === 'overview'
              ? 'text-blue-600 bg-blue-50'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <TrendingUp className="w-4 h-4" />
          <span>Overview</span>
        </button>

        <button
          type="button"
          onClick={() => handleMobileTabSwitch('content')}
          className={`flex flex-col items-center justify-center space-y-1 text-[11px] font-semibold py-1 px-2.5 rounded-lg transition-colors ${
            activeTab === 'content' && mobileTab !== 'preview'
              ? 'text-blue-600 bg-blue-50'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Content</span>
        </button>

        <button
          type="button"
          onClick={() => handleMobileTabSwitch('customize')}
          className={`flex flex-col items-center justify-center space-y-1 text-[11px] font-semibold py-1 px-2.5 rounded-lg transition-colors ${
            (activeTab === 'customize' || activeTab === 'style') && mobileTab !== 'preview'
              ? 'text-blue-600 bg-blue-50'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <Sliders className="w-4 h-4" />
          <span>Design</span>
        </button>

        <button
          type="button"
          onClick={() => handleMobileTabSwitch('ai')}
          className={`flex flex-col items-center justify-center space-y-1 text-[11px] font-semibold py-1 px-2.5 rounded-lg transition-colors ${
            activeTab === 'ai'
              ? 'text-emerald-600 bg-emerald-50'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>AI</span>
        </button>

        {isSplitPaneMode && (
          <button
            type="button"
            onClick={() => handleMobileTabSwitch('preview')}
            className={`flex flex-col items-center justify-center space-y-1 text-[11px] font-semibold py-1 px-2.5 rounded-lg transition-colors ${
              mobileTab === 'preview'
                ? 'text-blue-600 bg-blue-50'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <Eye className="w-4 h-4" />
            <span>Preview</span>
          </button>
        )}
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

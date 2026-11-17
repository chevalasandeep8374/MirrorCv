'use client';

import React from 'react';
import Link from 'next/link';
import { useResume, EditorTab } from '@/context/ResumeContext';
import { ResumeSelectorDropdown } from './header/ResumeSelectorDropdown';
import { DownloadDropdown } from './header/DownloadDropdown';
import { EditorOverflowMenu } from './header/EditorOverflowMenu';
import {
  ArrowLeft,
  CheckCircle2,
  Clock,
  AlertCircle,
  Undo2,
  Redo2,
  Sparkles,
  Sliders,
  FileText,
  TrendingUp,
} from 'lucide-react';

interface EditorHeaderProps {
  onOpenVersions?: () => void;
  onOpenShare?: () => void;
  onOpenAi?: () => void;
  onOpenAts?: () => void;
  onOpenTailor?: () => void;
}

export const EditorHeader: React.FC<EditorHeaderProps> = ({
  onOpenVersions,
  onOpenShare,
  onOpenAi,
  onOpenAts,
  onOpenTailor,
}) => {
  const {
    resumeId,
    title,
    saveStatus,
    activeTab,
    setActiveTab,
    canUndo,
    canRedo,
    undo,
    redo,
  } = useResume();

  const handleTabClick = (tab: EditorTab) => {
    setActiveTab(tab);
  };

  const isTabActive = (tab: EditorTab) => {
    if (tab === 'customize') {
      return activeTab === 'customize' || activeTab === 'style';
    }
    return activeTab === tab;
  };

  return (
    <header className="h-14 border-b border-slate-200 bg-white px-4 flex items-center justify-between z-30 select-none">
      <h1 className="sr-only">Resume Editor - {title || 'Untitled Resume'}</h1>
      {/* 1. Left: Back, Switcher Dropdown, Save Status */}
      <div className="flex items-center space-x-3">
        <Link
          href="/dashboard"
          className="p-1.5 text-slate-400 hover:text-slate-800 hover:bg-slate-100 rounded-xl transition-colors"
          title="Back to Dashboard"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>

        {/* In-header Resume Switcher Dropdown */}
        <ResumeSelectorDropdown
          currentResumeId={resumeId}
          currentTitle={title}
        />

        {/* Save Status Indicator */}
        <div className="flex items-center space-x-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100">
          {saveStatus === 'saved' && (
            <>
              <CheckCircle2 className="w-3 h-3 text-emerald-500" />
              <span className="text-slate-600 hidden sm:inline">Saved</span>
            </>
          )}
          {saveStatus === 'saving' && (
            <>
              <Clock className="w-3 h-3 text-blue-500 animate-spin" />
              <span className="text-blue-600 hidden sm:inline">Saving...</span>
            </>
          )}
          {saveStatus === 'unsaved' && (
            <>
              <div className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
              <span className="text-amber-600 hidden sm:inline">Unsaved</span>
            </>
          )}
          {saveStatus === 'conflict' && (
            <>
              <AlertCircle className="w-3 h-3 text-rose-500" />
              <span className="text-rose-600 hidden sm:inline">Conflict</span>
            </>
          )}
        </div>
      </div>

      {/* 2. Center: 4-Tab Navigation Shell */}
      <nav className="flex items-center bg-slate-100/90 p-1 rounded-2xl border border-slate-200/60 shadow-2xs">
        <button
          type="button"
          onClick={() => handleTabClick('overview')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl font-bold text-xs transition-all ${
            isTabActive('overview')
              ? 'bg-white text-blue-600 shadow-xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
          }`}
        >
          <TrendingUp className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Overview</span>
        </button>

        <button
          type="button"
          onClick={() => handleTabClick('content')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl font-bold text-xs transition-all ${
            isTabActive('content')
              ? 'bg-white text-blue-600 shadow-xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Content</span>
        </button>

        <button
          type="button"
          onClick={() => handleTabClick('customize')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl font-bold text-xs transition-all ${
            isTabActive('customize')
              ? 'bg-white text-blue-600 shadow-xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
          }`}
        >
          <Sliders className="w-3.5 h-3.5" />
          <span>Customize</span>
        </button>

        <button
          type="button"
          onClick={() => handleTabClick('ai')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl font-bold text-xs transition-all ${
            isTabActive('ai')
              ? 'bg-white text-emerald-600 shadow-xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5 text-emerald-500" />
          <span className="hidden sm:inline">AI Tools</span>
        </button>
      </nav>

      {/* 3. Right: Undo/Redo, Unified Download, Overflow Menu */}
      <div className="flex items-center space-x-2">
        <div className="hidden sm:flex items-center space-x-0.5">
          <button
            type="button"
            onClick={undo}
            disabled={!canUndo}
            className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-xl disabled:opacity-30 disabled:hover:bg-transparent transition-colors"
            title="Undo (Ctrl+Z)"
          >
            <Undo2 className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={redo}
            disabled={!canRedo}
            className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-xl disabled:opacity-30 disabled:hover:bg-transparent transition-colors"
            title="Redo (Ctrl+Y)"
          >
            <Redo2 className="w-4 h-4" />
          </button>
        </div>

        {/* Unified Download Dropdown Menu */}
        <DownloadDropdown />

        {/* Overflow Menu: Rename, Duplicate, Share, Versions, Shortcuts, Delete */}
        <EditorOverflowMenu
          onOpenVersions={onOpenVersions || (() => {})}
          onOpenShare={onOpenShare || (() => {})}
        />
      </div>
    </header>
  );
};

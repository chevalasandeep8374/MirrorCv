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
  LayoutGrid,
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
    <header className="h-14 border-b border-slate-200/90 bg-white px-4 flex items-center justify-between z-30 select-none shadow-[0_1px_2px_rgba(0,0,0,0.03)]">
      <h1 className="sr-only">Resume Editor - {title || 'Untitled Resume'}</h1>
      {/* 1. Left: Navigation Back & 4-Tab Navigation Shell */}
      <div className="flex items-center space-x-2 sm:space-x-3">
        <Link
          href="/dashboard"
          className="p-1.5 text-slate-400 hover:text-slate-800 hover:bg-slate-100 rounded-xl transition-colors"
          title="Back to Dashboard"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>

        {/* 4-Tab Navigation Shell */}
        <nav className="flex items-center space-x-1 sm:space-x-1.5">
          <button
            type="button"
            onClick={() => handleTabClick('overview')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full font-bold text-xs transition-all ${
              isTabActive('overview')
                ? 'bg-[#FFF0F5] text-[#FF2D6C] border border-[#FFD5DF] shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <LayoutGrid className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Overview</span>
          </button>

          <button
            type="button"
            onClick={() => handleTabClick('content')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full font-bold text-xs transition-all ${
              isTabActive('content')
                ? 'bg-[#FFF0F5] text-[#FF2D6C] border border-[#FFD5DF] shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Content</span>
          </button>

          <button
            type="button"
            onClick={() => handleTabClick('customize')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full font-bold text-xs transition-all ${
              isTabActive('customize')
                ? 'bg-[#FFF0F5] text-[#FF2D6C] border border-[#FFD5DF] shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>Customize</span>
          </button>

          <button
            type="button"
            onClick={() => handleTabClick('ai')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full font-bold text-xs transition-all ${
              isTabActive('ai')
                ? 'bg-[#FFF0F5] text-[#FF2D6C] border border-[#FFD5DF] shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">AI Tools</span>
          </button>
        </nav>
      </div>

      {/* 2. Right: Save Status, Switcher Dropdown, Undo/Redo, Unified Download, Overflow Menu */}
      <div className="flex items-center space-x-2 sm:space-x-2.5">
        {/* Subtle Save Status Indicator */}
        <div className="hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-slate-50 border border-slate-200/80">
          {saveStatus === 'saved' && (
            <>
              <CheckCircle2 className="w-3 h-3 text-emerald-500" />
              <span className="text-slate-600">Saved</span>
            </>
          )}
          {saveStatus === 'saving' && (
            <>
              <Clock className="w-3 h-3 text-[#FF2D6C] animate-spin" />
              <span className="text-[#FF2D6C]">Saving...</span>
            </>
          )}
          {saveStatus === 'unsaved' && (
            <>
              <div className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
              <span className="text-amber-600">Unsaved</span>
            </>
          )}
          {saveStatus === 'conflict' && (
            <>
              <AlertCircle className="w-3 h-3 text-rose-500" />
              <span className="text-rose-600">Conflict</span>
            </>
          )}
        </div>

        {/* Undo/Redo Buttons */}
        <div className="hidden lg:flex items-center space-x-0.5">
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

        {/* In-header Resume Switcher Dropdown */}
        <ResumeSelectorDropdown
          currentResumeId={resumeId}
          currentTitle={title}
        />

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

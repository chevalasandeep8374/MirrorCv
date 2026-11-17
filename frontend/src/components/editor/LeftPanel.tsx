'use client';

import React from 'react';
import { useResume } from '@/context/ResumeContext';
import { SectionList } from './content/SectionList';
import { CustomizeTab } from './customize/CustomizeTab';
import { CoverLetterPanel } from './cover-letter/CoverLetterPanel';
import { FileText, Sliders, Mail, AlertCircle, RefreshCw } from 'lucide-react';

export const LeftPanel: React.FC = () => {
  const { content, activeTab, setActiveTab, saveStatus, resolveConflict } = useResume();
  const isCoverLetter = Boolean(content.coverLetter);
  const isCustomizeActive = activeTab === 'customize' || activeTab === 'style';

  return (
    <aside className="w-full md:w-[480px] lg:w-[500px] flex-shrink-0 bg-slate-50 border-r border-slate-200 flex flex-col h-[calc(100vh-3.5rem)] select-none">
      {/* Tab Switcher */}
      <div className="h-12 border-b border-slate-200 bg-white px-4 flex items-center space-x-2">
        <button
          type="button"
          onClick={() => setActiveTab('content')}
          className={`flex-1 py-1.5 px-3 rounded-lg font-semibold text-xs flex items-center justify-center space-x-1.5 transition-all ${
            activeTab === 'content'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          {isCoverLetter ? <Mail className="w-3.5 h-3.5" /> : <FileText className="w-3.5 h-3.5" />}
          <span>{isCoverLetter ? 'Letter Content' : 'Resume Content'}</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('customize')}
          className={`flex-1 py-1.5 px-3 rounded-lg font-semibold text-xs flex items-center justify-center space-x-1.5 transition-all ${
            isCustomizeActive
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <Sliders className="w-3.5 h-3.5" />
          <span>Customize Design</span>
        </button>
      </div>

      {/* Version Conflict Resolution Banner */}
      {saveStatus === 'conflict' && (
        <div className="bg-rose-50 border-b border-rose-200 p-3 flex flex-col gap-2 text-xs text-rose-900 animate-in fade-in">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-bold">Version Conflict Detected</p>
              <p className="text-[11px] text-rose-700">This resume was modified in another tab or device. Choose how to resolve:</p>
            </div>
          </div>
          <div className="flex items-center gap-2 self-end">
            <button
              type="button"
              onClick={() => resolveConflict('reload')}
              className="px-2.5 py-1 bg-white border border-rose-300 rounded-lg font-bold text-rose-700 hover:bg-rose-100 shadow-2xs transition-colors"
            >
              Reload Latest
            </button>
            <button
              type="button"
              onClick={() => resolveConflict('overwrite')}
              className="px-2.5 py-1 bg-rose-600 text-white rounded-lg font-bold hover:bg-rose-700 shadow-2xs transition-colors"
            >
              Overwrite
            </button>
          </div>
        </div>
      )}

      {/* Tab Body */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'content' ? (
          isCoverLetter ? (
            <CoverLetterPanel />
          ) : (
            <SectionList />
          )
        ) : (
          <div className="h-full overflow-y-auto p-4">
            <CustomizeTab />
          </div>
        )}
      </div>
    </aside>
  );
};

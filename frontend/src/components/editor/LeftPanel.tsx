'use client';

import React from 'react';
import { useResume } from '@/context/ResumeContext';
import { SectionList } from './content/SectionList';
import { StylePanel } from './style/StylePanel';
import { CoverLetterPanel } from './cover-letter/CoverLetterPanel';
import { FileText, Sliders, Mail } from 'lucide-react';

export const LeftPanel: React.FC = () => {
  const { content, activeTab, setActiveTab } = useResume();
  const isCoverLetter = Boolean(content.coverLetter);

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
          onClick={() => setActiveTab('style')}
          className={`flex-1 py-1.5 px-3 rounded-lg font-semibold text-xs flex items-center justify-center space-x-1.5 transition-all ${
            activeTab === 'style'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <Sliders className="w-3.5 h-3.5" />
          <span>Style & Layout</span>
        </button>
      </div>

      {/* Tab Body */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'content' ? (
          isCoverLetter ? (
            <CoverLetterPanel />
          ) : (
            <SectionList />
          )
        ) : (
          <StylePanel />
        )}
      </div>
    </aside>
  );
};

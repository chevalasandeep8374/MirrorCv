'use client';

import React from 'react';
import { useResume } from '@/context/ResumeContext';
import { SectionList } from './content/SectionList';
import { EditEntryView } from './content/EditEntryView';
import { CustomizeTab } from './customize/CustomizeTab';
import { CoverLetterPanel } from './cover-letter/CoverLetterPanel';
import { AiResumeCopilot } from './ai/AiResumeCopilot';
import { AlertCircle } from 'lucide-react';

interface LeftPanelProps {
  onOpenTailorModal?: () => void;
  onOpenAtsModal?: () => void;
}

export const LeftPanel: React.FC<LeftPanelProps> = ({
  onOpenTailorModal,
  onOpenAtsModal,
}) => {
  const {
    content,
    activeTab,
    activeEditingItem,
    setActiveEditingItem,
    saveStatus,
    resolveConflict,
  } = useResume();
  const isCoverLetter = Boolean(content.coverLetter);

  return (
    <aside className="w-full md:w-[540px] lg:w-[580px] xl:w-[620px] flex-shrink-0 bg-[#F8F9FA] border-r border-slate-200/90 flex flex-col h-[calc(100vh-3.5rem)] select-none isolate-paint">
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
          ) : activeEditingItem ? (
            <EditEntryView
              sectionId={activeEditingItem.sectionId}
              itemId={activeEditingItem.itemId}
              onClose={() => setActiveEditingItem(null)}
            />
          ) : (
            <SectionList />
          )
        ) : activeTab === 'ai' ? (
          <AiResumeCopilot
            onOpenTailorModal={onOpenTailorModal}
            onOpenAtsModal={onOpenAtsModal}
          />
        ) : (
          <div className="h-full overflow-y-auto p-4">
            <CustomizeTab />
          </div>
        )}
      </div>
    </aside>
  );
};

'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import { ResumeProvider } from '@/context/ResumeContext';
import { EditorHeader } from '@/components/editor/EditorHeader';
import { LeftPanel } from '@/components/editor/LeftPanel';
import { LivePreviewPane } from '@/components/editor/preview/LivePreviewPane';

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
      <div className="h-screen w-screen flex flex-col overflow-hidden bg-slate-100">
        {/* Top App Header */}
        <EditorHeader />

        {/* Split Viewport */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Edit Controls (Content & Style tabs) */}
          <LeftPanel />

          {/* Right Live Document Preview */}
          <LivePreviewPane />
        </div>
      </div>
    </ResumeProvider>
  );
}

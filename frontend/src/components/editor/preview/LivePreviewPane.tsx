'use client';

import React from 'react';
import { useResume } from '@/context/ResumeContext';
import { ResumeDocument } from '@/components/resume-renderer/ResumeDocument';

export const LivePreviewPane: React.FC = () => {
  const { content, style, zoom } = useResume();

  return (
    <div className="flex-1 bg-slate-200/70 overflow-auto p-8 flex justify-center items-start min-h-full">
      <div
        className="transition-transform duration-150 origin-top flex flex-col items-center shadow-lg"
        style={{
          transform: `scale(${zoom})`,
          marginBottom: '80px',
        }}
      >
        <ResumeDocument content={content} style={style} />
      </div>
    </div>
  );
};

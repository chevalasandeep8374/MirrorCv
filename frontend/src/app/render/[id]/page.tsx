'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import axios from 'axios';
import { ResumeDocument } from '@/components/resume-renderer/ResumeDocument';
import { Resume } from '@/types/resume';
import { defaultResumeContent, classicSingleColumnPreset } from '@/lib/presets';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function RenderResumePage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const id = params?.id as string;
  const renderToken = searchParams.get('render_token');
  const token = searchParams.get('token');

  const [resume, setResume] = useState<Resume | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchResume() {
      if (!id) return;
      try {
        if (renderToken) {
          // Secure single-use, 60s render token endpoint
          const res = await axios.get<Resume>(
            `${API_BASE_URL}/api/resumes/${id}/render-data?render_token=${encodeURIComponent(renderToken)}`
          );
          setResume(res.data);
        } else {
          // Fallback legacy token or public view
          const headers: Record<string, string> = {};
          if (token) {
            headers['Authorization'] = `Bearer ${token}`;
          }
          const res = await axios.get<Resume>(`${API_BASE_URL}/api/resumes/${id}`, {
            headers,
          });
          setResume(res.data);
        }
      } catch (err: unknown) {
        console.error('Failed to load resume for print', err);
        setError('Failed to load resume document.');
      } finally {
        setLoading(false);
      }
    }

    fetchResume();
  }, [id, renderToken, token]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-white text-gray-500 font-sans text-sm">
        Preparing document for PDF export...
      </div>
    );
  }

  if (error || !resume) {
    return (
      <div className="flex h-screen items-center justify-center bg-white text-red-500 font-sans text-sm">
        {error || 'Resume not found.'}
      </div>
    );
  }

  return (
    <div className="w-full bg-white flex flex-col items-center">
      <ResumeDocument
        content={resume.content || defaultResumeContent}
        style={resume.style || classicSingleColumnPreset}
        isPrint={true}
      />
    </div>
  );
}

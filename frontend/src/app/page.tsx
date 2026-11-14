'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import { FileText, Plus, Sparkles, ArrowRight, Loader2, Palette } from 'lucide-react';

interface ResumeSummary {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export default function HomePage() {
  const router = useRouter();
  const [resumes, setResumes] = useState<ResumeSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    async function loadResumes() {
      try {
        const res = await apiClient.get<ResumeSummary[]>('/resumes');
        setResumes(res.data);
      } catch (err) {
        console.error('Failed to load resumes:', err);
      } finally {
        setLoading(false);
      }
    }
    loadResumes();
  }, []);

  const handleCreate = async () => {
    setCreating(true);
    try {
      const res = await apiClient.post('/resumes', {
        title: 'New Resume',
      });
      router.push(`/editor/${res.data.id}`);
    } catch (err) {
      console.error('Failed to create resume:', err);
      setCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Navbar */}
      <header className="border-b border-slate-200 bg-white sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold shadow-sm shadow-blue-500/20">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <span className="text-lg font-bold tracking-tight text-slate-900">
                MirrorCV
              </span>
              <span className="ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                Foundation
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleCreate}
              disabled={creating}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm rounded-lg shadow-sm transition disabled:opacity-50"
            >
              {creating ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Plus className="w-4 h-4" />
              )}
              <span>Create Resume</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-10 flex-1 w-full">
        <div className="mb-8">
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            My Resumes
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Resumes with decoupled content schema and style tokens. Live preview and 1:1 PDF export.
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-20 text-slate-400">
            <Loader2 className="w-8 h-8 animate-spin" />
          </div>
        ) : resumes.length === 0 ? (
          <div className="border-2 border-dashed border-slate-200 rounded-2xl p-12 text-center bg-white">
            <div className="w-14 h-14 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-7 h-7" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-1">
              No resumes found
            </h3>
            <p className="text-sm text-slate-500 max-w-sm mx-auto mb-6">
              Create your first resume or run the database seed script to populate realistic templates.
            </p>
            <button
              onClick={handleCreate}
              disabled={creating}
              className="inline-flex items-center space-x-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm rounded-xl shadow-sm transition"
            >
              <Plus className="w-4 h-4" />
              <span>Create My First Resume</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resumes.map((resume) => (
              <div
                key={resume.id}
                className="group border border-slate-200 hover:border-blue-400 rounded-2xl p-6 bg-white shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="p-2 rounded-lg bg-blue-50 text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                      <FileText className="w-5 h-5" />
                    </span>
                    <span className="text-xs text-slate-400 font-medium">
                      {new Date(resume.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h2 className="text-lg font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                    {resume.title}
                  </h2>
                  <p className="text-xs text-slate-400 mt-1 truncate">
                    ID: {resume.id}
                  </p>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
                  <Link
                    href={`/editor/${resume.id}`}
                    className="inline-flex items-center space-x-1.5 text-sm font-semibold text-blue-600 hover:text-blue-700"
                  >
                    <span>Open Editor</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                  </Link>

                  <Link
                    href={`/render/${resume.id}`}
                    target="_blank"
                    className="text-xs text-slate-500 hover:text-slate-800"
                  >
                    Print View
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

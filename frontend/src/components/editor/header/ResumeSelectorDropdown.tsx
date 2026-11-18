'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { getActiveRepository } from '@/repositories';
import { ResumeSummary } from '@/types/resume';
import {
  FileText,
  ChevronDown,
  Search,
  Plus,
  Copy,
  Check,
  FolderOpen,
  Loader2,
} from 'lucide-react';

interface ResumeSelectorDropdownProps {
  currentResumeId: string;
  currentTitle: string;
}

export const ResumeSelectorDropdown: React.FC<ResumeSelectorDropdownProps> = ({
  currentResumeId,
  currentTitle,
}) => {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [resumes, setResumes] = useState<ResumeSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [creating, setCreating] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const loadResumes = async () => {
    setLoading(true);
    try {
      const repo = await getActiveRepository();
      const list = await repo.list(false);
      setResumes(list);
    } catch (e) {
      console.error('Failed to load resumes:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = () => {
    if (!isOpen) {
      loadResumes();
    }
    setIsOpen((prev) => !prev);
  };

  const handleCreateNew = async () => {
    setCreating(true);
    try {
      const repo = await getActiveRepository();
      const newResume = await repo.create({
        title: 'New Resume',
      });
      router.push(`/editor/${newResume.id}`);
      setIsOpen(false);
    } catch (e) {
      alert('Failed to create resume. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  const handleDuplicateCurrent = async () => {
    setCreating(true);
    try {
      const repo = await getActiveRepository();
      const duplicated = await repo.duplicate(currentResumeId);
      router.push(`/editor/${duplicated.id}`);
      setIsOpen(false);
    } catch (e) {
      alert('Failed to duplicate resume.');
    } finally {
      setCreating(false);
    }
  };

  const filteredResumes = resumes.filter((r) =>
    r.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        type="button"
        id="resumeSwitcherBtn"
        onClick={handleToggle}
        className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md border border-slate-200 bg-white hover:bg-slate-50 text-slate-800 text-xs font-medium transition-colors shadow-2xs max-w-[200px] cursor-pointer"
        title="Switch or create resume"
      >
        <FileText className="w-3.5 h-3.5 text-slate-400 shrink-0" />
        <span className="truncate">{currentTitle || 'Demo Resume'}</span>
        <ChevronDown className="w-3.5 h-3.5 text-slate-400 shrink-0" />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1.5 w-72 glass-2 rounded-card shadow-card border border-border-subtle z-50 overflow-hidden animate-in fade-in zoom-in-95">
          {/* Search Box */}
          <div className="p-2.5 border-b border-slate-100 bg-slate-50">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search resumes..."
                className="w-full text-xs pl-8 pr-2.5 py-1.5 bg-white border border-slate-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 font-medium"
                autoFocus
              />
            </div>
          </div>

          {/* Resumes List */}
          <div className="max-h-56 overflow-y-auto p-1.5 space-y-0.5">
            {loading ? (
              <div className="py-6 flex flex-col items-center justify-center text-xs text-slate-400 gap-1.5">
                <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                <span>Loading your resumes...</span>
              </div>
            ) : filteredResumes.length === 0 ? (
              <div className="py-5 text-center text-xs text-slate-400">
                No resumes match &quot;{search}&quot;
              </div>
            ) : (
              filteredResumes.map((r) => {
                const isActive = r.id === currentResumeId;
                return (
                  <button
                    key={r.id}
                    type="button"
                    onClick={() => {
                      if (!isActive) {
                        router.push(`/editor/${r.id}`);
                      }
                      setIsOpen(false);
                    }}
                    className={`w-full flex items-center justify-between p-2 rounded-xl text-xs text-left transition-colors ${
                      isActive
                        ? 'bg-blue-50 text-blue-900 font-bold'
                        : 'hover:bg-slate-50 text-slate-700 font-medium'
                    }`}
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      <FileText
                        className={`w-3.5 h-3.5 shrink-0 ${
                          isActive ? 'text-blue-600' : 'text-slate-400'
                        }`}
                      />
                      <span className="truncate">{r.title || 'Untitled Resume'}</span>
                    </div>
                    {isActive && <Check className="w-3.5 h-3.5 text-blue-600 shrink-0" />}
                  </button>
                );
              })
            )}
          </div>

          {/* Actions: Create New & Duplicate */}
          <div className="p-2 border-t border-slate-100 bg-slate-50/80 space-y-1">
            <button
              type="button"
              onClick={handleCreateNew}
              disabled={creating}
              className="w-full flex items-center gap-2 px-3 py-1.5 text-xs font-semibold text-blue-600 hover:bg-blue-50 rounded-xl transition-colors disabled:opacity-50"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>+ Create New Resume</span>
            </button>

            <button
              type="button"
              onClick={handleDuplicateCurrent}
              disabled={creating}
              className="w-full flex items-center gap-2 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded-xl transition-colors disabled:opacity-50"
            >
              <Copy className="w-3.5 h-3.5" />
              <span>Duplicate Current Resume</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

'use client';

import React, { useEffect, useState, useMemo } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import { getActiveRepository, localRepo, supabaseRepo } from '@/repositories';
import { ResumeSummary } from '@/types/resume';
import {
  FileText,
  Plus,
  Sparkles,
  ArrowRight,
  Loader2,
  Copy,
  Archive,
  ArchiveRestore,
  Trash2,
  Edit2,
  Tag,
  Folder,
  Search,
  Check,
  X,
  ExternalLink,
  MoreVertical,
  Clock,
  Briefcase,
  Layers,
  Mail,
  Upload,
  User,
} from 'lucide-react';
import { CoverLetterGenerateModal } from '@/components/editor/cover-letter/CoverLetterGenerateModal';
import { ImportModal } from '@/components/dashboard/ImportModal';
import { AccountSettingsModal } from '@/components/dashboard/AccountSettingsModal';

export default function HomePage() {
  const router = useRouter();
  const [resumes, setResumes] = useState<ResumeSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [activeTab, setActiveTab] = useState<'all' | 'archived'>('all');
  const [selectedFolder, setSelectedFolder] = useState<string>('all');
  const [selectedTag, setSelectedTag] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Editing state for rename/tag modal
  const [editingResume, setEditingResume] = useState<ResumeSummary | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editTargetTitle, setEditTargetTitle] = useState('');
  const [editFolder, setEditFolder] = useState('');
  const [editTagsInput, setEditTagsInput] = useState('');
  const [savingEdit, setSavingEdit] = useState(false);

  // Action busy states
  const [actionInProgress, setActionInProgress] = useState<string | null>(null);
  const [coverLetterModalResumeId, setCoverLetterModalResumeId] = useState<string | null>(null);
  const [importModalOpen, setImportModalOpen] = useState(false);
  const [accountModalOpen, setAccountModalOpen] = useState(false);

  // Local storage migration state
  const [hasLocalResumes, setHasLocalResumes] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [importingLocal, setImportingLocal] = useState(false);
  const [importSuccessMsg, setImportSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    setHasLocalResumes(localRepo.hasResumes());
    setIsLoggedIn(Boolean(localStorage.getItem('mirrorcv_token')));
  }, []);

  const handleImportLocal = async () => {
    setImportingLocal(true);
    try {
      const res = await supabaseRepo.importLocalResumes(localRepo.getAll());
      setImportSuccessMsg(`Imported ${res.importedCount} resume(s) to cloud successfully!`);
      setHasLocalResumes(localRepo.hasResumes());
      await loadResumes();
      setTimeout(() => setImportSuccessMsg(null), 5000);
    } catch (err) {
      console.error('Failed to import local resumes:', err);
      alert('Could not import local resumes. Please sign in to cloud first.');
    } finally {
      setImportingLocal(false);
    }
  };

  // Load resumes via active repository
  const loadResumes = async () => {
    try {
      setLoading(true);
      const isArchived = activeTab === 'archived';
      const repo = await getActiveRepository();
      const list = await repo.list(isArchived);
      setResumes(list);
    } catch (err) {
      console.error('Failed to load resumes:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadResumes();
  }, [activeTab]);

  // Derive unique folders and tags
  const allFolders = useMemo(() => {
    const set = new Set<string>();
    resumes.forEach((r) => {
      if (r.folder && r.folder.trim()) set.add(r.folder.trim());
    });
    return Array.from(set).sort();
  }, [resumes]);

  const allTags = useMemo(() => {
    const set = new Set<string>();
    resumes.forEach((r) => {
      if (Array.isArray(r.tags)) {
        r.tags.forEach((t) => t && set.add(t.trim()));
      }
    });
    return Array.from(set).sort();
  }, [resumes]);

  // Filtered list
  const filteredResumes = useMemo(() => {
    return resumes.filter((r) => {
      if (selectedFolder !== 'all' && r.folder !== selectedFolder) return false;
      if (selectedTag !== 'all') {
        if (!Array.isArray(r.tags) || !r.tags.includes(selectedTag)) return false;
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const titleMatch = r.title.toLowerCase().includes(q);
        const jobMatch = (r.target_job_title || '').toLowerCase().includes(q);
        const tagMatch = (r.tags || []).some((t) => t.toLowerCase().includes(q));
        if (!titleMatch && !jobMatch && !tagMatch) return false;
      }
      return true;
    });
  }, [resumes, selectedFolder, selectedTag, searchQuery]);

  const handleCreate = async () => {
    setCreating(true);
    try {
      const repo = await getActiveRepository();
      const newResume = await repo.create({
        title: 'New Resume',
        target_job_title: 'Software Engineer',
      });
      router.push(`/editor/${newResume.id}`);
    } catch (err) {
      console.error('Failed to create resume:', err);
      setCreating(false);
    }
  };

  const handleDuplicate = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setActionInProgress(id);
    try {
      const repo = await getActiveRepository();
      await repo.duplicate(id);
      await loadResumes();
    } catch (err) {
      console.error('Failed to duplicate resume:', err);
    } finally {
      setActionInProgress(null);
    }
  };

  const handleArchiveToggle = async (id: string, isArchived: boolean, e: React.MouseEvent) => {
    e.stopPropagation();
    setActionInProgress(id);
    try {
      const repo = await getActiveRepository();
      await repo.update(id, { is_archived: !isArchived });
      await loadResumes();
    } catch (err) {
      console.error('Failed to archive/unarchive resume:', err);
    } finally {
      setActionInProgress(null);
    }
  };

  const handleDelete = async (id: string, title: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm(`Are you sure you want to delete "${title}"?`)) return;
    setActionInProgress(id);
    try {
      const repo = await getActiveRepository();
      await repo.delete(id);
      await loadResumes();
    } catch (err) {
      console.error('Failed to delete resume:', err);
    } finally {
      setActionInProgress(null);
    }
  };

  const handleTailorJump = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setActionInProgress(id);
    try {
      const res = await apiClient.post(`/resumes/${id}/tailor-jump`);
      // Navigate to /tailor with the template ID preloaded
      router.push(`/tailor?template_id=${res.data.template_id}`);
    } catch (err) {
      console.error('Failed to launch tailor from resume:', err);
      router.push('/tailor');
    } finally {
      setActionInProgress(null);
    }
  };

  const openEditModal = (resume: ResumeSummary, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingResume(resume);
    setEditTitle(resume.title);
    setEditTargetTitle(resume.target_job_title || '');
    setEditFolder(resume.folder || '');
    setEditTagsInput((resume.tags || []).join(', '));
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingResume) return;
    setSavingEdit(true);
    try {
      const parsedTags = editTagsInput
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean);

      const repo = await getActiveRepository();
      await repo.update(editingResume.id, {
        title: editTitle.trim() || 'Untitled Resume',
        target_job_title: editTargetTitle.trim() || null,
        folder: editFolder.trim() || null,
        tags: parsedTags,
      });

      setEditingResume(null);
      await loadResumes();
    } catch (err) {
      console.error('Failed to update resume metadata:', err);
    } finally {
      setSavingEdit(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Navbar */}
      <header className="border-b border-slate-200 bg-white sticky top-0 z-20 shadow-2xs">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold shadow-sm shadow-blue-500/20">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <span className="text-lg font-bold tracking-tight text-slate-900">
                MirrorCV
              </span>
              <span className="ml-2 text-xs font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                Phase 3 Parity
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <Link
              href="/tailor"
              className="inline-flex items-center space-x-2 px-3.5 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold text-xs rounded-xl border border-indigo-200 transition"
            >
              <Sparkles className="w-4 h-4 text-indigo-600" />
              <span>Tailor from Upload (PDF/DOCX)</span>
            </Link>

            <button
              onClick={() => setAccountModalOpen(true)}
              className="px-3 py-1.5 text-xs font-semibold text-slate-700 hover:text-slate-900 border border-slate-200 rounded-lg hover:bg-slate-100 transition inline-flex items-center gap-1.5"
              title="Account Settings & GDPR Data Export"
            >
              <User className="w-3.5 h-3.5 text-slate-500" />
              <span>Account</span>
            </button>

            <button
              onClick={() => {
                if (typeof window !== 'undefined') {
                  const token = localStorage.getItem('mirrorcv_token');
                  if (token) {
                    localStorage.removeItem('mirrorcv_token');
                    localStorage.removeItem('mirrorcv_user');
                    window.location.reload();
                  } else {
                    router.push('/login');
                  }
                }
              }}
              className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 border border-slate-200 rounded-lg hover:bg-slate-100 transition"
            >
              {isLoggedIn ? 'Sign Out' : 'Sign In'}
            </button>

            <button
              onClick={() => setImportModalOpen(true)}
              className="inline-flex items-center space-x-1.5 px-3.5 py-2 bg-white border border-slate-200 hover:border-slate-300 text-slate-700 font-bold text-xs rounded-xl shadow-2xs transition"
              title="Import JSON Resume or LinkedIn ZIP"
            >
              <Upload className="w-3.5 h-3.5 text-slate-500" />
              <span>Import</span>
            </button>

            <button
              onClick={handleCreate}
              disabled={creating}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-sm transition disabled:opacity-50"
            >
              {creating ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Plus className="w-4 h-4" />
              )}
              <span>New Resume</span>
            </button>
          </div>
        </div>
      </header>

      {/* Local Resumes Migration Banner */}
      {hasLocalResumes && (
        <div className="bg-amber-50 border-b border-amber-200 px-6 py-3">
          <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-sm">
            <div className="flex items-center space-x-2 text-amber-900">
              <Sparkles className="w-4 h-4 text-amber-600 shrink-0" />
              <span>
                <strong>Local Resumes Found:</strong> You have resumes stored in your browser storage. Import them to your cloud account to sync across devices.
              </span>
            </div>
            <div className="flex items-center space-x-3">
              <button
                type="button"
                onClick={handleImportLocal}
                disabled={importingLocal}
                className="px-3.5 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold shadow-xs disabled:opacity-50 transition"
              >
                {importingLocal ? 'Importing...' : 'Import to Cloud'}
              </button>
              <button
                type="button"
                onClick={() => setHasLocalResumes(false)}
                className="text-xs text-amber-800 hover:text-amber-950 font-medium"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {importSuccessMsg && (
        <div className="bg-emerald-50 border-b border-emerald-200 px-6 py-2.5 text-center text-xs font-semibold text-emerald-800">
          {importSuccessMsg}
        </div>
      )}

      {/* Main Dashboard Body */}
      <main className="max-w-7xl mx-auto px-6 py-8 flex-1 w-full">
        {/* Top Control Bar: Search, Filters & Tabs */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
              <span>My Resume Dashboard</span>
              <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-slate-200/80 text-slate-700">
                {filteredResumes.length} {filteredResumes.length === 1 ? 'doc' : 'docs'}
              </span>
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Manage multiple tailored versions, organize with tags & folders, and generate identical-look PDFs.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Search Input */}
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                placeholder="Search resumes or target job..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 pr-3 py-1.5 text-xs bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-1 focus:ring-blue-500 w-64 shadow-2xs"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Folder Dropdown */}
            {allFolders.length > 0 && (
              <div className="flex items-center space-x-1.5 bg-white border border-slate-200 rounded-xl px-2.5 py-1 text-xs shadow-2xs">
                <Folder className="w-3.5 h-3.5 text-slate-500" />
                <select
                  value={selectedFolder}
                  onChange={(e) => setSelectedFolder(e.target.value)}
                  className="bg-transparent font-medium text-slate-700 focus:outline-none cursor-pointer"
                >
                  <option value="all">All Folders</option>
                  {allFolders.map((f) => (
                    <option key={f} value={f}>
                      {f}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Tag Filter */}
            {allTags.length > 0 && (
              <div className="flex items-center space-x-1.5 bg-white border border-slate-200 rounded-xl px-2.5 py-1 text-xs shadow-2xs">
                <Tag className="w-3.5 h-3.5 text-slate-500" />
                <select
                  value={selectedTag}
                  onChange={(e) => setSelectedTag(e.target.value)}
                  className="bg-transparent font-medium text-slate-700 focus:outline-none cursor-pointer"
                >
                  <option value="all">All Tags</option>
                  {allTags.map((t) => (
                    <option key={t} value={t}>
                      #{t}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Active vs Archived Tabs */}
            <div className="bg-slate-200/80 p-0.5 rounded-xl flex text-xs font-semibold">
              <button
                onClick={() => setActiveTab('all')}
                className={`px-3 py-1 rounded-lg transition ${
                  activeTab === 'all'
                    ? 'bg-white text-slate-900 shadow-2xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Active
              </button>
              <button
                onClick={() => setActiveTab('archived')}
                className={`px-3 py-1 rounded-lg transition ${
                  activeTab === 'archived'
                    ? 'bg-white text-slate-900 shadow-2xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Archived
              </button>
            </div>
          </div>
        </div>

        {/* Resume Grid */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 text-slate-400">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600 mb-2" />
            <span className="text-xs font-medium">Loading your resumes...</span>
          </div>
        ) : filteredResumes.length === 0 ? (
          <div className="border-2 border-dashed border-slate-200 rounded-3xl p-16 text-center bg-white shadow-2xs">
            <div className="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-1">
              {searchQuery || selectedFolder !== 'all' || selectedTag !== 'all'
                ? 'No resumes match your filter criteria'
                : activeTab === 'archived'
                ? 'No archived resumes'
                : 'No resumes created yet'}
            </h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mb-6">
              {activeTab === 'archived'
                ? 'Resumes you archive will safely appear here instead of cluttering your main view.'
                : 'Create your first custom resume or tailor one from your existing master PDF/DOCX.'}
            </p>
            {activeTab !== 'archived' && (
              <button
                onClick={handleCreate}
                disabled={creating}
                className="inline-flex items-center space-x-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-sm transition"
              >
                <Plus className="w-4 h-4" />
                <span>Create New Resume</span>
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredResumes.map((resume) => {
              const isBusy = actionInProgress === resume.id;

              return (
                <div
                  key={resume.id}
                  onClick={() => router.push(`/editor/${resume.id}`)}
                  className="group relative bg-white border border-slate-200 hover:border-blue-400 rounded-2xl p-5 shadow-2xs hover:shadow-lg transition-all duration-200 flex flex-col justify-between cursor-pointer overflow-hidden"
                >
                  {/* Top Header Card */}
                  <div>
                    {/* Badges Bar */}
                    <div className="flex items-center justify-between gap-2 mb-3">
                      <div className="flex items-center space-x-1.5 flex-wrap gap-y-1">
                        {/* Tailored From Badge */}
                        {resume.tailored_from_id && (
                          <span
                            title={`Tailored from "${resume.tailored_from_title || 'Master Resume'}"`}
                            className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-purple-50 text-purple-700 border border-purple-200 text-[10px] font-bold"
                          >
                            <Sparkles className="w-3 h-3 text-purple-600" />
                            <span>Tailored Copy</span>
                          </span>
                        )}

                        {/* Folder Badge */}
                        {resume.folder && (
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 text-[10px] font-semibold">
                            <Folder className="w-3 h-3 text-slate-500" />
                            <span>{resume.folder}</span>
                          </span>
                        )}
                      </div>

                      <div className="flex items-center space-x-1 text-slate-400">
                        <Clock className="w-3 h-3" />
                        <span className="text-[10px] font-medium">
                          {new Date(resume.updated_at || resume.updatedAt || Date.now()).toLocaleDateString(undefined, {
                            month: 'short',
                            day: 'numeric',
                          })}
                        </span>
                      </div>
                    </div>

                    {/* Resume Title */}
                    <h2 className="text-base font-extrabold text-slate-900 group-hover:text-blue-600 transition-colors line-clamp-1">
                      {resume.title}
                    </h2>

                    {/* Target Job Title */}
                    <div className="flex items-center space-x-1.5 text-xs text-slate-500 mt-1">
                      <Briefcase className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="truncate font-medium">
                        {resume.target_job_title || 'General Resume'}
                      </span>
                    </div>

                    {/* Tags */}
                    {resume.tags && resume.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2.5">
                        {resume.tags.map((t, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-0.5 rounded-md bg-slate-50 text-slate-600 border border-slate-200 text-[10px] font-medium"
                          >
                            #{t}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Thumbnail / Visual Placeholder Box */}
                  <div className="my-4 h-36 bg-slate-100 rounded-xl border border-slate-200/80 overflow-hidden relative group-hover:border-blue-200 transition-colors">
                    <iframe
                      src={`/render/${resume.id}`}
                      className="w-[800px] h-[1000px] pointer-events-none scale-[0.25] origin-top-left border-none bg-white"
                      title={resume.title}
                      loading="lazy"
                    />
                    <div className="absolute inset-0 bg-transparent" />
                  </div>

                  {/* Bottom Action Footer */}
                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                    {/* Primary Jump Action & Cover Letter */}
                    <div className="flex items-center space-x-1.5">
                      <button
                        type="button"
                        title="Tailor a new version for another job description"
                        onClick={(e) => handleTailorJump(resume.id, e)}
                        disabled={isBusy}
                        className="inline-flex items-center space-x-1 px-2 py-1 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold text-[11px] transition"
                      >
                        <Sparkles className="w-3 h-3 text-indigo-600" />
                        <span>Tailor</span>
                      </button>

                      <button
                        type="button"
                        title="Generate a matching cover letter from this resume"
                        onClick={(e) => {
                          e.stopPropagation();
                          setCoverLetterModalResumeId(resume.id);
                        }}
                        disabled={isBusy}
                        className="inline-flex items-center space-x-1 px-2 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 font-bold text-[11px] transition"
                      >
                        <Mail className="w-3 h-3 text-blue-600" />
                        <span>Letter</span>
                      </button>
                    </div>

                    {/* Action Icon Group */}
                    <div className="flex items-center space-x-1 text-slate-500">
                      {/* Duplicate */}
                      <button
                        type="button"
                        title="Duplicate resume"
                        onClick={(e) => handleDuplicate(resume.id, e)}
                        disabled={isBusy}
                        className="p-1.5 rounded-lg hover:text-slate-900 hover:bg-slate-100 transition"
                      >
                        <Copy className="w-3.5 h-3.5" />
                      </button>

                      {/* Edit Meta (Rename/Tag) */}
                      <button
                        type="button"
                        title="Rename and manage tags"
                        onClick={(e) => openEditModal(resume, e)}
                        disabled={isBusy}
                        className="p-1.5 rounded-lg hover:text-slate-900 hover:bg-slate-100 transition"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>

                      {/* Archive / Unarchive */}
                      <button
                        type="button"
                        title={resume.is_archived ? 'Unarchive resume' : 'Archive resume'}
                        onClick={(e) => handleArchiveToggle(resume.id, Boolean(resume.is_archived ?? resume.isArchived), e)}
                        disabled={isBusy}
                        className="p-1.5 rounded-lg hover:text-slate-900 hover:bg-slate-100 transition"
                      >
                        {resume.is_archived ? (
                          <ArchiveRestore className="w-3.5 h-3.5 text-blue-600" />
                        ) : (
                          <Archive className="w-3.5 h-3.5" />
                        )}
                      </button>

                      {/* Delete */}
                      <button
                        type="button"
                        title="Delete resume"
                        onClick={(e) => handleDelete(resume.id, resume.title, e)}
                        disabled={isBusy}
                        className="p-1.5 rounded-lg hover:text-rose-600 hover:bg-rose-50 transition"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>

      {/* Edit Metadata Modal */}
      {editingResume && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
          <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-md p-6 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-slate-900">
                Edit Resume Details
              </h3>
              <button
                onClick={() => setEditingResume(null)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveEdit} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Resume Title
                </label>
                <input
                  type="text"
                  required
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-1 focus:ring-blue-500 font-sans"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Target Job Title
                </label>
                <input
                  type="text"
                  placeholder="e.g. Senior Frontend Engineer"
                  value={editTargetTitle}
                  onChange={(e) => setEditTargetTitle(e.target.value)}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-1 focus:ring-blue-500 font-sans"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Folder
                </label>
                <input
                  type="text"
                  placeholder="e.g. FAANG, Startups, Q4 Applications"
                  value={editFolder}
                  onChange={(e) => setEditFolder(e.target.value)}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-1 focus:ring-blue-500 font-sans"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  placeholder="e.g. python, remote, tech"
                  value={editTagsInput}
                  onChange={(e) => setEditTagsInput(e.target.value)}
                  className="w-full p-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-1 focus:ring-blue-500 font-sans"
                />
              </div>

              <div className="pt-2 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setEditingResume(null)}
                  className="px-4 py-2 font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingEdit}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-sm transition disabled:opacity-50"
                >
                  {savingEdit ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Cover Letter Generator Modal */}
      {coverLetterModalResumeId && (
        <CoverLetterGenerateModal
          resumeId={coverLetterModalResumeId}
          isOpen={Boolean(coverLetterModalResumeId)}
          onClose={() => setCoverLetterModalResumeId(null)}
        />
      )}

      {/* Resume Import Modal (JSON Resume & LinkedIn ZIP) */}
      <ImportModal
        isOpen={importModalOpen}
        onClose={() => setImportModalOpen(false)}
        onSuccess={loadResumes}
      />

      {/* Account Settings & GDPR Export Modal */}
      <AccountSettingsModal
        isOpen={accountModalOpen}
        onClose={() => setAccountModalOpen(false)}
      />
    </div>
  );
}

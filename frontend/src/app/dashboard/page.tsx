'use client';

import React, { useEffect, useState, useMemo } from 'react';
import Link from 'next/link';
import { MirrorCvLogo } from '@/components/brand/MirrorCvLogo';
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
  ArrowUpRight,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';
import { CoverLetterGenerateModal } from '@/components/editor/cover-letter/CoverLetterGenerateModal';
import { ImportModal } from '@/components/dashboard/ImportModal';
import { AccountSettingsModal } from '@/components/dashboard/AccountSettingsModal';

export default function DashboardPage() {
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
  const [mounted, setMounted] = useState(false);
  const [hasLocalResumes, setHasLocalResumes] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [importingLocal, setImportingLocal] = useState(false);
  const [importSuccessMsg, setImportSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    setMounted(true);
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
    <div className="min-h-screen bg-page flex flex-col font-sans selection:bg-primary/10 selection:text-primary">
      {/* MirrorCV Glass-1 Navigation Bar */}
      <header className="sticky top-0 z-40 glass-1 border-b border-border-subtle px-6 md:px-12 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <MirrorCvLogo size="md" asLink href="/" />
          <span className="hidden sm:inline-block text-[11px] font-bold uppercase tracking-wider text-primary bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200">
            Workspace
          </span>
        </div>

        <nav className="flex items-center gap-3">
          <Link
            href="/"
            className="text-xs font-semibold text-slate-600 hover:text-slate-950 transition-colors px-3 py-1.5 rounded-btn"
          >
            Home
          </Link>
          <Link
            href="/templates"
            className="text-xs font-semibold text-slate-600 hover:text-slate-950 transition-colors px-3 py-1.5 rounded-btn hidden sm:inline-block"
          >
            Templates
          </Link>
          <Link
            href="/tailor"
            className="text-xs font-semibold text-slate-600 hover:text-slate-950 transition-colors px-3 py-1.5 rounded-btn hidden md:inline-block"
          >
            Tailor
          </Link>

          <button
            onClick={() => setImportModalOpen(true)}
            className="btn-secondary !text-xs !py-1.5 !px-3.5 inline-flex items-center gap-1.5"
            title="Import Existing Resume (PDF, DOCX, JSON, etc.)"
          >
            <Upload className="w-3.5 h-3.5 text-primary" />
            <span>Import Existing Resume</span>
          </button>

          <button
            onClick={() => setAccountModalOpen(true)}
            className="p-2 text-slate-600 hover:text-slate-950 hover:bg-slate-100 rounded-btn transition-colors border border-border-subtle bg-white"
            title="Account Settings"
          >
            <User className="w-4 h-4" />
          </button>

          <button
            onClick={handleCreate}
            disabled={creating}
            className="btn-primary !text-xs !py-1.5 !px-4 shadow-btn"
          >
            {creating ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Plus className="w-3.5 h-3.5" />
            )}
            <span>New Document</span>
          </button>
        </nav>
      </header>

      {/* Cloud Migration Notification Banner (if local data exists) */}
      {mounted && hasLocalResumes && isLoggedIn && (
        <div className="bg-paper-surface border-b border-paper-border px-6 md:px-12 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3 text-xs text-ink-body">
            <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
            <span>You have local offline resumes saved in your browser storage.</span>
          </div>
          <button
            onClick={handleImportLocal}
            disabled={importingLocal}
            className="btn-secondary !text-xs !py-1 !px-3 !rounded-sm"
          >
            {importingLocal ? 'Syncing...' : 'Sync to Cloud'}
          </button>
        </div>
      )}

      {/* Main Workspace Area */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-6 md:px-12 py-10 space-y-8">
        {/* Workspace Title & Quick Stats */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-border-subtle">
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-primary mb-1.5">
              Document Portfolio
            </div>
            <h1 className="font-heading font-extrabold text-3xl md:text-4xl text-slate-950 tracking-tight">
              Your Documents
            </h1>
            <p className="text-sm text-slate-600 mt-1">
              Select a resume to edit styling tokens, calibrate typography, or export pixel-perfect PDFs.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => setImportModalOpen(true)}
              className="px-3.5 py-2 text-xs font-bold rounded-full bg-white text-slate-700 border border-border-subtle hover:border-slate-300 hover:text-slate-900 shadow-xs flex items-center gap-1.5 transition-all"
            >
              <Upload className="w-3.5 h-3.5 text-primary" />
              <span>Import Existing Resume</span>
            </button>
            <button
              onClick={() => setActiveTab('all')}
              className={`px-4 py-2 text-xs font-bold rounded-full transition-all ${
                activeTab === 'all'
                  ? 'bg-primary text-white shadow-btn'
                  : 'bg-white text-slate-600 border border-border-subtle hover:text-slate-900'
              }`}
            >
              Active ({resumes.filter((r) => !r.is_archived).length})
            </button>
            <button
              onClick={() => setActiveTab('archived')}
              className={`px-4 py-2 text-xs font-bold rounded-full transition-all ${
                activeTab === 'archived'
                  ? 'bg-primary text-white shadow-btn'
                  : 'bg-white text-slate-600 border border-border-subtle hover:text-slate-900'
              }`}
            >
              Archived ({resumes.filter((r) => r.is_archived).length})
            </button>
          </div>
        </div>

        {/* Filter & Search Bar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by title, target role, or tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 text-xs bg-white border border-border-subtle rounded-btn text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs font-semibold"
              >
                Clear
              </button>
            )}
          </div>

          {allFolders.length > 0 && (
            <select
              value={selectedFolder}
              onChange={(e) => setSelectedFolder(e.target.value)}
              className="text-xs bg-white border border-border-subtle rounded-btn px-3 py-2.5 text-slate-700 focus:outline-none focus:border-primary"
            >
              <option value="all">All Folders</option>
              {allFolders.map((f) => (
                <option key={f} value={f}>
                  Folder: {f}
                </option>
              ))}
            </select>
          )}

          {allTags.length > 0 && (
            <select
              value={selectedTag}
              onChange={(e) => setSelectedTag(e.target.value)}
              className="text-xs bg-white border border-border-subtle rounded-btn px-3 py-2.5 text-slate-700 focus:outline-none focus:border-primary"
            >
              <option value="all">All Tags</option>
              {allTags.map((t) => (
                <option key={t} value={t}>
                  #{t}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Document Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-4">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="bg-white border border-border-subtle rounded-card p-6 h-48 animate-pulse flex flex-col justify-between"
              >
                <div className="space-y-2.5">
                  <div className="h-4 bg-slate-200 rounded w-3/4" />
                  <div className="h-3 bg-slate-100 rounded w-1/2" />
                </div>
                <div className="h-8 bg-slate-100 rounded-btn w-full" />
              </div>
            ))}
          </div>
        ) : filteredResumes.length === 0 ? (
          <div className="bg-white border border-border-subtle rounded-card p-12 text-center space-y-4 max-w-lg mx-auto my-12 shadow-sm">
            <div className="w-12 h-12 rounded-full bg-slate-50 border border-border-subtle flex items-center justify-center mx-auto text-slate-400">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-heading font-extrabold text-lg text-slate-900">No documents found</h3>
              <p className="text-xs text-slate-500 mt-1">
                {searchQuery || selectedFolder !== 'all' || selectedTag !== 'all'
                  ? 'Try clearing your search or filter tags.'
                  : 'Start composing your first precision resume.'}
              </p>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
              <button onClick={handleCreate} disabled={creating} className="btn-primary !text-xs !py-2 !px-5 shadow-btn flex items-center gap-1.5">
                <Plus className="w-3.5 h-3.5" />
                <span>Create New Resume</span>
              </button>
              <button
                onClick={() => setImportModalOpen(true)}
                className="btn-secondary !text-xs !py-2 !px-5 flex items-center gap-1.5"
              >
                <Upload className="w-3.5 h-3.5 text-primary" />
                <span>Import Existing Resume</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredResumes.map((resume) => {
              const isBusy = actionInProgress === resume.id;
              return (
                <div
                  key={resume.id}
                  onClick={() => router.push(`/editor/${resume.id}`)}
                  className="bg-white border border-border-subtle rounded-card group p-5 cursor-pointer hover:border-slate-300 hover:shadow-card transition-all flex flex-col justify-between h-56 relative shadow-sm"
                >
                  {/* Top Bar: Title, Target Job, Quick Menu */}
                  <div>
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <h3 className="font-heading font-bold text-base text-slate-900 truncate group-hover:text-primary transition-colors">
                          {resume.title}
                        </h3>
                        {resume.target_job_title && (
                          <p className="text-xs text-slate-500 truncate mt-0.5 flex items-center gap-1.5">
                            <Briefcase className="w-3 h-3 text-slate-400" />
                            <span>{resume.target_job_title}</span>
                          </p>
                        )}
                      </div>

                      <div className="flex items-center gap-1 opacity-70 group-hover:opacity-100">
                        <button
                          type="button"
                          onClick={(e) => openEditModal(resume, e)}
                          className="p-1 text-slate-400 hover:text-slate-700 rounded hover:bg-slate-100"
                          title="Rename & Organize"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          type="button"
                          onClick={(e) => handleDuplicate(resume.id, e)}
                          disabled={isBusy}
                          className="p-1 text-slate-400 hover:text-slate-700 rounded hover:bg-slate-100"
                          title="Duplicate"
                        >
                          <Copy className="w-3.5 h-3.5" />
                        </button>
                        <button
                          type="button"
                          onClick={(e) => handleArchiveToggle(resume.id, Boolean(resume.is_archived), e)}
                          disabled={isBusy}
                          className="p-1 text-slate-400 hover:text-slate-700 rounded hover:bg-slate-100"
                          title={resume.is_archived ? 'Restore' : 'Archive'}
                        >
                          {resume.is_archived ? (
                            <ArchiveRestore className="w-3.5 h-3.5" />
                          ) : (
                            <Archive className="w-3.5 h-3.5" />
                          )}
                        </button>
                        <button
                          type="button"
                          onClick={(e) => handleDelete(resume.id, resume.title, e)}
                          disabled={isBusy}
                          className="p-1 text-slate-400 hover:text-rose-600 rounded hover:bg-rose-50"
                          title="Delete"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>

                    {/* Metadata Tags & Folder */}
                    <div className="flex flex-wrap items-center gap-1.5 mt-3">
                      {resume.folder && (
                        <span className="text-[10px] font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200 flex items-center gap-1">
                          <Folder className="w-2.5 h-2.5" /> {resume.folder}
                        </span>
                      )}
                      {(resume.tags || []).slice(0, 3).map((t) => (
                        <span
                          key={t}
                          className="text-[10px] font-semibold text-pill-purple bg-purple-50 px-2 py-0.5 rounded border border-purple-100"
                        >
                          #{t}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Bottom Actions Bar */}
                  <div className="pt-3 border-t border-border-subtle flex items-center justify-between">
                    <span className="text-[11px] text-slate-400 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(resume.updated_at || Date.now()).toLocaleDateString()}</span>
                    </span>

                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setCoverLetterModalResumeId(resume.id);
                        }}
                        className="text-[11px] font-bold text-slate-500 hover:text-primary transition-colors"
                        title="Generate Grounded Cover Letter"
                      >
                        Cover Letter
                      </button>
                      <button
                        type="button"
                        onClick={(e) => handleTailorJump(resume.id, e)}
                        className="text-[11px] font-bold text-primary hover:underline flex items-center gap-0.5"
                      >
                        <span>Tailor</span>
                        <ArrowUpRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>

      {/* Edit Resume Metadata Modal */}
      {editingResume && (
        <div className="fixed inset-0 z-50 glass-scrim flex items-center justify-center p-4">
          <div className="bg-white border border-border-subtle rounded-card p-6 max-w-md w-full shadow-card space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-border-subtle">
              <h3 className="font-heading font-extrabold text-base text-slate-900">Edit Document Details</h3>
              <button
                onClick={() => setEditingResume(null)}
                className="text-slate-400 hover:text-slate-700 text-sm p-1 rounded hover:bg-slate-100"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveEdit} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">Resume Title</label>
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-btn bg-white border border-border-subtle text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                  required
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Target Job Title</label>
                <input
                  type="text"
                  value={editTargetTitle}
                  onChange={(e) => setEditTargetTitle(e.target.value)}
                  placeholder="e.g. Lead Distributed Systems Engineer"
                  className="w-full px-3 py-2 rounded-btn bg-white border border-border-subtle text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Folder (Grouping)</label>
                <input
                  type="text"
                  value={editFolder}
                  onChange={(e) => setEditFolder(e.target.value)}
                  placeholder="e.g. Big Tech, Startups, 2026"
                  className="w-full px-3 py-2 rounded-btn bg-white border border-border-subtle text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Tags (Comma-separated)</label>
                <input
                  type="text"
                  value={editTagsInput}
                  onChange={(e) => setEditTagsInput(e.target.value)}
                  placeholder="e.g. typescript, rust, kubernetes"
                  className="w-full px-3 py-2 rounded-btn bg-white border border-border-subtle text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                />
              </div>

              <div className="pt-3 border-t border-border-subtle flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setEditingResume(null)}
                  className="btn-secondary !text-xs !py-1.5 !px-3.5"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingEdit}
                  className="btn-primary !text-xs !py-1.5 !px-4 shadow-btn"
                >
                  {savingEdit ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Auxiliary Modals */}
      {coverLetterModalResumeId && (
        <CoverLetterGenerateModal
          isOpen={true}
          resumeId={coverLetterModalResumeId}
          onClose={() => setCoverLetterModalResumeId(null)}
        />
      )}

      {importModalOpen && (
        <ImportModal
          isOpen={importModalOpen}
          onClose={() => setImportModalOpen(false)}
          onSuccess={() => loadResumes()}
        />
      )}

      {accountModalOpen && (
        <AccountSettingsModal
          isOpen={accountModalOpen}
          onClose={() => setAccountModalOpen(false)}
        />
      )}
    </div>
  );
}

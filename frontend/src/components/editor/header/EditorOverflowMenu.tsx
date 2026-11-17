'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useResume } from '@/context/ResumeContext';
import { getActiveRepository } from '@/repositories';
import {
  MoreVertical,
  Edit2,
  Copy,
  Share2,
  History,
  Command,
  Trash2,
  Check,
} from 'lucide-react';
import { KeyboardShortcutsModal } from '../KeyboardShortcutsModal';

interface EditorOverflowMenuProps {
  onOpenVersions: () => void;
  onOpenShare: () => void;
}

export const EditorOverflowMenu: React.FC<EditorOverflowMenuProps> = ({
  onOpenVersions,
  onOpenShare,
}) => {
  const router = useRouter();
  const { resumeId, title, setTitle } = useResume();
  const [isOpen, setIsOpen] = useState(false);
  const [shortcutsOpen, setShortcutsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
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

  const handleRename = () => {
    setIsOpen(false);
    const newName = prompt('Enter new title for this resume:', title);
    if (newName && newName.trim()) {
      setTitle(newName.trim());
    }
  };

  const handleDuplicate = async () => {
    setIsOpen(false);
    try {
      const repo = await getActiveRepository();
      const dup = await repo.duplicate(resumeId);
      router.push(`/editor/${dup.id}`);
    } catch (e) {
      alert('Failed to duplicate resume.');
    }
  };

  const handleDelete = async () => {
    setIsOpen(false);
    if (confirm(`Are you sure you want to permanently delete "${title}"? This cannot be undone.`)) {
      try {
        const repo = await getActiveRepository();
        await repo.delete(resumeId);
        router.push('/');
      } catch (e) {
        alert('Failed to delete resume.');
      }
    }
  };

  return (
    <>
      <div className="relative" ref={menuRef}>
        <button
          type="button"
          onClick={() => setIsOpen((prev) => !prev)}
          className="p-2 text-slate-600 hover:text-slate-900 bg-white hover:bg-slate-50 border border-slate-200/90 rounded-xl shadow-2xs transition-colors cursor-pointer"
          title="More actions"
        >
          <MoreVertical className="w-4 h-4" />
        </button>

        {isOpen && (
          <div className="absolute right-0 top-full mt-1.5 w-52 glass-2 rounded-card shadow-card border border-border-subtle z-50 p-1.5 space-y-0.5 animate-in fade-in zoom-in-95">
            <button
              type="button"
              onClick={handleRename}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded-xl transition-colors text-left"
            >
              <Edit2 className="w-3.5 h-3.5 text-slate-400" />
              <span>Rename Resume</span>
            </button>

            <button
              type="button"
              onClick={handleDuplicate}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded-xl transition-colors text-left"
            >
              <Copy className="w-3.5 h-3.5 text-slate-400" />
              <span>Duplicate Resume</span>
            </button>

            <button
              type="button"
              onClick={() => {
                setIsOpen(false);
                onOpenShare();
              }}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded-xl transition-colors text-left"
            >
              <Share2 className="w-3.5 h-3.5 text-slate-400" />
              <span>Share Public Link</span>
            </button>

            <button
              type="button"
              onClick={() => {
                setIsOpen(false);
                onOpenVersions();
              }}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded-xl transition-colors text-left"
            >
              <History className="w-3.5 h-3.5 text-slate-400" />
              <span>Version History</span>
            </button>

            <div className="h-px bg-slate-100 my-1" />

            <button
              type="button"
              onClick={() => {
                setIsOpen(false);
                setShortcutsOpen(true);
              }}
              className="w-full flex items-center justify-between px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded-xl transition-colors text-left"
            >
              <div className="flex items-center gap-2.5">
                <Command className="w-3.5 h-3.5 text-slate-400" />
                <span>Shortcuts</span>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">Ctrl+/</span>
            </button>

            <div className="h-px bg-slate-100 my-1" />

            <button
              type="button"
              onClick={handleDelete}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-rose-600 hover:bg-rose-50 rounded-xl transition-colors text-left"
            >
              <Trash2 className="w-3.5 h-3.5 text-rose-500" />
              <span>Delete Resume</span>
            </button>
          </div>
        )}
      </div>

      <KeyboardShortcutsModal
        isOpen={shortcutsOpen}
        onClose={() => setShortcutsOpen(false)}
      />
    </>
  );
};

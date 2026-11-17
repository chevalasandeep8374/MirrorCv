'use client';

import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { arrayMove } from '@dnd-kit/sortable';
import { ResumeContent, ResumeSection, SectionItem, SectionType, HeaderContent, BulletItem } from '@/types/content';
import { ResumeStyle } from '@/types/style';
import { Resume } from '@/types/resume';
import { classicSingleColumnPreset, defaultResumeContent } from '@/lib/presets';
import { formatStructuredDate } from '@/lib/migration';
import {
  getActiveRepository,
  localRepo,
  supabaseRepo,
  VersionConflictError,
  ImportResult,
} from '@/repositories';

type SaveStatus = 'saved' | 'saving' | 'unsaved' | 'error' | 'conflict';
export type EditorTab = 'overview' | 'content' | 'customize' | 'style' | 'ai' | 'templates';

interface ResumeContextType {
  resumeId: string;
  title: string;
  content: ResumeContent;
  style: ResumeStyle;
  version: number;
  saveStatus: SaveStatus;
  lastSaved: Date | null;
  zoom: number;
  activeTab: EditorTab;
  activeSectionId: string | null;
  loading: boolean;
  hasLocalResumes: boolean;

  // Conflict & Migration
  resolveConflict: (action: 'reload' | 'overwrite') => Promise<void>;
  importLocalResumes: () => Promise<ImportResult>;

  // View / UI
  setZoom: (zoom: number | ((prev: number) => number)) => void;
  setActiveTab: (tab: EditorTab) => void;
  setActiveSectionId: (id: string | null) => void;
  setTitle: (title: string) => void;

  // Content Actions
  updateContent: (content: ResumeContent) => void;
  updateHeader: (header: Partial<HeaderContent>) => void;
  reorderSections: (oldIndex: number, newIndex: number) => void;
  toggleSectionVisibility: (sectionId: string) => void;
  toggleSectionPageBreak: (sectionId: string) => void;
  removeSection: (sectionId: string) => void;
  duplicateSection: (sectionId: string) => void;
  addSection: (type: SectionType, title?: string) => void;
  updateSectionTitle: (sectionId: string, title: string) => void;
  addItem: (sectionId: string) => void;
  duplicateItem: (sectionId: string, itemId: string) => void;
  removeItem: (sectionId: string, itemId: string) => void;
  reorderItems: (sectionId: string, oldIndex: number, newIndex: number) => void;
  updateItem: (sectionId: string, itemId: string, itemData: Partial<SectionItem>) => void;
  addBullet: (sectionId: string, itemId: string) => void;
  removeBullet: (sectionId: string, itemId: string, bulletId: string) => void;
  reorderBullets: (sectionId: string, itemId: string, oldIndex: number, newIndex: number) => void;
  updateBullet: (
    sectionId: string,
    itemId: string,
    bulletId: string,
    patch: string | Partial<BulletItem>
  ) => void;

  // Undo / Redo
  canUndo: boolean;
  canRedo: boolean;
  undo: () => void;
  redo: () => void;
  startStyleDrag: () => void;
  endStyleDrag: () => void;

  // One-Page Fit
  onePageFitActive: boolean;
  onePageFitWarning: string | null;
  toggleOnePageFit: () => void;

  // Style Actions
  updateStyle: (style: ResumeStyle) => void;
  applyPreset: (preset: ResumeStyle) => void;

  // JSON Import / Export
  exportContentJson: () => void;
  importContentJson: (imported: ResumeContent) => void;
  exportStyleJson: () => void;
  importStyleJson: (imported: ResumeStyle) => void;

  // Save
  saveNow: () => Promise<void>;
}

const ResumeContext = createContext<ResumeContextType | undefined>(undefined);

export const ResumeProvider: React.FC<{
  resumeId: string;
  initialResume?: Resume;
  children: React.ReactNode;
}> = ({ resumeId, initialResume, children }) => {
  const [loading, setLoading] = useState(!initialResume);
  const [title, setTitleState] = useState(initialResume?.title || 'Untitled Resume');
  const [content, setContentState] = useState<ResumeContent>(
    initialResume?.content || defaultResumeContent
  );
  const [style, setStyleState] = useState<ResumeStyle>(
    initialResume?.style || classicSingleColumnPreset
  );
  const [version, setVersion] = useState<number>(initialResume?.version ?? 1);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('saved');
  const [hasLocalResumes, setHasLocalResumes] = useState<boolean>(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(new Date());
  const [zoom, setZoom] = useState(1);
  const [activeTab, setActiveTab] = useState<EditorTab>('content');
  const [activeSectionId, setActiveSectionId] = useState<string | null>(null);

  // Undo / Redo history
  interface HistorySnapshot {
    content: ResumeContent;
    style: ResumeStyle;
  }
  const undoStackRef = useRef<HistorySnapshot[]>([]);
  const redoStackRef = useRef<HistorySnapshot[]>([]);
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);
  const dragStartStyleRef = useRef<ResumeStyle | null>(null);

  const startStyleDrag = useCallback(() => {
    if (!dragStartStyleRef.current) {
      dragStartStyleRef.current = JSON.parse(JSON.stringify(style));
    }
  }, [style]);

  const endStyleDrag = useCallback(() => {
    if (dragStartStyleRef.current) {
      const prevStyle = dragStartStyleRef.current;
      dragStartStyleRef.current = null;
      if (JSON.stringify(prevStyle) !== JSON.stringify(style)) {
        undoStackRef.current.push({
          content: JSON.parse(JSON.stringify(content)),
          style: prevStyle,
        });
        if (undoStackRef.current.length > 50) undoStackRef.current.shift();
        redoStackRef.current = [];
        setCanUndo(true);
        setCanRedo(false);
      }
    }
  }, [content, style]);

  // One-Page Fit
  const [onePageFitActive, setOnePageFitActive] = useState(false);
  const [onePageFitWarning, setOnePageFitWarning] = useState<string | null>(null);

  const isInitialMount = useRef(true);
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Helper to push history
  const pushContentWithHistory = useCallback((newContent: ResumeContent | ((prev: ResumeContent) => ResumeContent)) => {
    setContentState((prev) => {
      const next = typeof newContent === 'function' ? newContent(prev) : newContent;
      if (next !== prev) {
        undoStackRef.current.push({
          content: prev,
          style: JSON.parse(JSON.stringify(style)),
        });
        if (undoStackRef.current.length > 50) undoStackRef.current.shift();
        redoStackRef.current = [];
        setCanUndo(true);
        setCanRedo(false);
      }
      return next;
    });
  }, [style]);

  const undo = useCallback(() => {
    if (undoStackRef.current.length === 0) return;
    const previous = undoStackRef.current.pop()!;
    redoStackRef.current.push({
      content: JSON.parse(JSON.stringify(content)),
      style: JSON.parse(JSON.stringify(style)),
    });
    setContentState(previous.content);
    setStyleState(previous.style);
    setCanUndo(undoStackRef.current.length > 0);
    setCanRedo(true);
  }, [content, style]);

  const redo = useCallback(() => {
    if (redoStackRef.current.length === 0) return;
    const next = redoStackRef.current.pop()!;
    undoStackRef.current.push({
      content: JSON.parse(JSON.stringify(content)),
      style: JSON.parse(JSON.stringify(style)),
    });
    setContentState(next.content);
    setStyleState(next.style);
    setCanUndo(true);
    setCanRedo(redoStackRef.current.length > 0);
  }, [content, style]);

  // Keyboard shortcut listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      const isInput = target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA');

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
        if (!isInput) {
          e.preventDefault();
          if (e.shiftKey) redo();
          else undo();
        }
      } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'y') {
        if (!isInput) {
          e.preventDefault();
          redo();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [undo, redo]);

  // Check if local storage has resumes that can be migrated
  useEffect(() => {
    setHasLocalResumes(localRepo.hasResumes());
  }, []);

  // Fetch resume if not provided as initial prop
  useEffect(() => {
    if (initialResume) return;

    async function fetchResume() {
      try {
        setLoading(true);
        const repo = await getActiveRepository();
        const data = await repo.get(resumeId);
        if (data) {
          setTitleState(data.title || 'Untitled Resume');
          setContentState(data.content || defaultResumeContent);
          setStyleState(data.style || classicSingleColumnPreset);
          setVersion(data.version ?? 1);
        }
      } catch (err) {
        console.error('Failed to load resume:', err);
        setSaveStatus('error');
      } finally {
        setLoading(false);
      }
    }

    fetchResume();
  }, [resumeId, initialResume]);

  // Autosave execution function with optimistic locking
  const executeSave = useCallback(
    async (
      curTitle: string,
      curContent: ResumeContent,
      curStyle: ResumeStyle,
      forceOverwrite = false
    ) => {
      setSaveStatus('saving');
      try {
        const repo = await getActiveRepository();
        const updated = await repo.update(resumeId, {
          title: curTitle,
          content: curContent,
          style: curStyle,
          expected_version: forceOverwrite ? undefined : version,
        });
        setVersion(updated.version ?? version + 1);
        setSaveStatus('saved');
        setLastSaved(new Date());
      } catch (err: unknown) {
        if (err instanceof VersionConflictError || (err as { code?: string })?.code === 'VERSION_CONFLICT') {
          console.warn('Optimistic lock conflict detected for resume:', resumeId);
          setSaveStatus('conflict');
        } else {
          console.error('Autosave error:', err);
          setSaveStatus('error');
        }
      }
    },
    [resumeId, version]
  );

  // Trigger debounced autosave when title, content, or style changes
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }

    setSaveStatus('unsaved');
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    saveTimeoutRef.current = setTimeout(() => {
      executeSave(title, content, style);
    }, 1000);

    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [title, content, style, executeSave]);

  const saveNow = async () => {
    if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    await executeSave(title, content, style);
  };

  const resolveConflict = useCallback(
    async (action: 'reload' | 'overwrite') => {
      if (action === 'reload') {
        try {
          setLoading(true);
          const repo = await getActiveRepository();
          const latest = await repo.get(resumeId);
          if (latest) {
            setTitleState(latest.title);
            setContentState(latest.content);
            setStyleState(latest.style);
            setVersion(latest.version ?? 1);
            setSaveStatus('saved');
          }
        } catch (e) {
          console.error('Failed to reload latest resume:', e);
          setSaveStatus('error');
        } finally {
          setLoading(false);
        }
      } else if (action === 'overwrite') {
        await executeSave(title, content, style, true);
      }
    },
    [resumeId, executeSave, title, content, style]
  );

  const importLocalResumes = useCallback(async (): Promise<ImportResult> => {
    const res = await supabaseRepo.importLocalResumes(localRepo.getAll());
    setHasLocalResumes(localRepo.hasResumes());
    return res;
  }, []);

  const setTitle = (newTitle: string) => {
    setTitleState(newTitle);
  };

  const updateContent = (newContent: ResumeContent) => {
    setContentState(newContent);
  };

  const updateStyle = (newStyle: ResumeStyle) => {
    setStyleState(newStyle);
  };

  const applyPreset = (preset: ResumeStyle) => {
    undoStackRef.current.push({
      content: JSON.parse(JSON.stringify(content)),
      style: JSON.parse(JSON.stringify(style)),
    });
    if (undoStackRef.current.length > 50) undoStackRef.current.shift();
    redoStackRef.current = [];
    setCanUndo(true);
    setCanRedo(false);
    setStyleState(preset);
  };

  // Header update
  const toggleSectionPageBreak = (sectionId: string) => {
    pushContentWithHistory((prev) => ({
      ...prev,
      sections: prev.sections.map((s) =>
        s.id === sectionId ? { ...s, pageBreakBefore: !s.pageBreakBefore } : s
      ),
    }));
  };

  const toggleOnePageFit = () => {
    if (!onePageFitActive) {
      setStyleState((prev) => ({
        ...prev,
        typography: {
          ...prev.typography,
          fontSizeScale: 0.92,
          lineHeight: 1.32,
        },
        spacing: {
          ...prev.spacing,
          sectionSpacing: 9,
          itemSpacing: 5,
          bulletSpacing: 1.5,
          headerBottomSpacing: 12,
        },
        margins: {
          ...prev.margins,
          top: 24,
          bottom: 24,
          left: 28,
          right: 28,
        },
      }));
      setOnePageFitActive(true);
    } else {
      setStyleState((prev) => ({
        ...prev,
        typography: {
          ...prev.typography,
          fontSizeScale: 1.0,
          lineHeight: 1.45,
        },
        spacing: {
          ...prev.spacing,
          sectionSpacing: 14,
          itemSpacing: 8,
          bulletSpacing: 3,
          headerBottomSpacing: 16,
        },
        margins: {
          ...prev.margins,
          top: 36,
          bottom: 36,
          left: 42,
          right: 42,
        },
      }));
      setOnePageFitActive(false);
      setOnePageFitWarning(null);
    }
  };

  const updateHeader = (patch: Partial<HeaderContent>) => {
    pushContentWithHistory((prev) => ({
      ...prev,
      header: {
        ...prev.header,
        ...patch,
      },
    }));
  };

  // Section actions
  const reorderSections = (oldIndex: number, newIndex: number) => {
    pushContentWithHistory((prev) => ({
      ...prev,
      sections: arrayMove(prev.sections, oldIndex, newIndex),
    }));
  };

  const toggleSectionVisibility = (sectionId: string) => {
    pushContentWithHistory((prev) => ({
      ...prev,
      sections: prev.sections.map((s) =>
        s.id === sectionId ? { ...s, visible: !s.visible } : s
      ),
    }));
  };

  const removeSection = (sectionId: string) => {
    pushContentWithHistory((prev) => ({
      ...prev,
      sections: prev.sections.filter((s) => s.id !== sectionId),
    }));
    if (activeSectionId === sectionId) setActiveSectionId(null);
  };

  const duplicateSection = (sectionId: string) => {
    pushContentWithHistory((prev) => {
      const idx = prev.sections.findIndex((s) => s.id === sectionId);
      if (idx === -1) return prev;
      const original = prev.sections[idx];
      const clonedId = `sec-${Date.now()}`;
      const cloned: ResumeSection = {
        ...original,
        id: clonedId,
        title: `${original.title} (Copy)`,
        items: original.items.map((item) => ({
          ...item,
          id: `item-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
          bullets: item.bullets.map((b) => ({
            ...b,
            id: `b-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
          })),
        })),
      };
      const updated = [...prev.sections];
      updated.splice(idx + 1, 0, cloned);
      return {
        ...prev,
        sections: updated,
      };
    });
  };

  const addSection = (type: SectionType, title?: string) => {
    const id = `sec-${Date.now()}`;
    const defaultTitles: Record<SectionType, string> = {
      summary: 'Professional Summary',
      experience: 'Work Experience',
      skills: 'Skills',
      education: 'Education',
      projects: 'Projects',
      certifications: 'Certifications',
      custom: 'Additional Information',
      languages: 'Languages',
      awards: 'Honors & Awards',
      publications: 'Publications',
      volunteering: 'Volunteering & Leadership',
      interests: 'Interests & Activities',
      references: 'References',
      links: 'Portfolio & Links',
    };

    const newSection: ResumeSection = {
      id,
      type,
      title: title || defaultTitles[type] || 'New Section',
      visible: true,
      items: [
        {
          id: `item-${Date.now()}`,
          title: '',
          subtitle: '',
          location: '',
          dateRange: '',
          bullets: [{ id: `b-${Date.now()}`, text: 'Enter bullet item here...' }],
        },
      ],
    };

    pushContentWithHistory((prev) => ({
      ...prev,
      sections: [...prev.sections, newSection],
    }));
    setActiveSectionId(id);
  };

  const updateSectionTitle = (sectionId: string, newTitle: string) => {
    pushContentWithHistory((prev) => ({
      ...prev,
      sections: prev.sections.map((s) =>
        s.id === sectionId ? { ...s, title: newTitle } : s
      ),
    }));
  };

  // Item actions
  const addItem = (sectionId: string) => {
    const newItem: SectionItem = {
      id: `item-${Date.now()}`,
      title: 'New Position / Project',
      subtitle: 'Company / Institution',
      location: '',
      dateRange: 'Year - Present',
      bullets: [{ id: `b-${Date.now()}`, text: 'Key contribution or achievement' }],
    };

    pushContentWithHistory((prev) => ({
      ...prev,
      sections: prev.sections.map((s) =>
        s.id === sectionId ? { ...s, items: [...(s.items || []), newItem] } : s
      ),
    }));
  };

  const removeItem = (sectionId: string, itemId: string) => {
    pushContentWithHistory((prev) => ({
      ...prev,
      sections: prev.sections.map((s) =>
        s.id === sectionId
          ? { ...s, items: s.items.filter((item) => item.id !== itemId) }
          : s
      ),
    }));
  };

  const duplicateItem = (sectionId: string, itemId: string) => {
    pushContentWithHistory((prev) => ({
      ...prev,
      sections: prev.sections.map((s) => {
        if (s.id !== sectionId) return s;
        const idx = s.items.findIndex((item) => item.id === itemId);
        if (idx === -1) return s;
        const orig = s.items[idx];
        const cloned: SectionItem = {
          ...orig,
          id: `item-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
          bullets: orig.bullets.map((b) => ({
            ...b,
            id: `b-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
          })),
        };
        const updated = [...s.items];
        updated.splice(idx + 1, 0, cloned);
        return { ...s, items: updated };
      }),
    }));
  };

  const reorderItems = (sectionId: string, oldIndex: number, newIndex: number) => {
    pushContentWithHistory((prev) => ({
      ...prev,
      sections: prev.sections.map((s) =>
        s.id === sectionId ? { ...s, items: arrayMove(s.items, oldIndex, newIndex) } : s
      ),
    }));
  };

  const updateItem = (
    sectionId: string,
    itemId: string,
    itemData: Partial<SectionItem>
  ) => {
    let patch = { ...itemData };
    if (patch.dates && !patch.dateRange) {
      patch.dateRange = formatStructuredDate(patch.dates, style.dateFormat || 'MM/YYYY');
    }
    pushContentWithHistory((prev) => ({
      ...prev,
      sections: prev.sections.map((s) =>
        s.id === sectionId
          ? {
              ...s,
              items: s.items.map((item) =>
                item.id === itemId ? { ...item, ...patch } : item
              ),
            }
          : s
      ),
    }));
  };

  // Bullet actions
  const addBullet = (sectionId: string, itemId: string) => {
    const newBullet = {
      id: `b-${Date.now()}`,
      text: 'New bullet point',
    };

    pushContentWithHistory((prev) => ({
      ...prev,
      sections: prev.sections.map((s) =>
        s.id === sectionId
          ? {
              ...s,
              items: s.items.map((item) =>
                item.id === itemId
                  ? { ...item, bullets: [...(item.bullets || []), newBullet] }
                  : item
              ),
            }
          : s
      ),
    }));
  };

  const removeBullet = (sectionId: string, itemId: string, bulletId: string) => {
    pushContentWithHistory((prev) => ({
      ...prev,
      sections: prev.sections.map((s) =>
        s.id === sectionId
          ? {
              ...s,
              items: s.items.map((item) =>
                item.id === itemId
                  ? { ...item, bullets: item.bullets.filter((b) => b.id !== bulletId) }
                  : item
              ),
            }
          : s
      ),
    }));
  };

  const reorderBullets = (
    sectionId: string,
    itemId: string,
    oldIndex: number,
    newIndex: number
  ) => {
    pushContentWithHistory((prev) => ({
      ...prev,
      sections: prev.sections.map((s) =>
        s.id === sectionId
          ? {
              ...s,
              items: s.items.map((item) =>
                item.id === itemId
                  ? { ...item, bullets: arrayMove(item.bullets, oldIndex, newIndex) }
                  : item
              ),
            }
          : s
      ),
    }));
  };

  const updateBullet = (
    sectionId: string,
    itemId: string,
    bulletId: string,
    patch: string | Partial<BulletItem>
  ) => {
    const patchObj = typeof patch === 'string' ? { text: patch } : patch;

    pushContentWithHistory((prev) => ({
      ...prev,
      sections: prev.sections.map((s) =>
        s.id === sectionId
          ? {
              ...s,
              items: s.items.map((item) =>
                item.id === itemId
                  ? {
                      ...item,
                      bullets: item.bullets.map((b) =>
                        b.id === bulletId ? { ...b, ...patchObj } : b
                      ),
                    }
                  : item
              ),
            }
          : s
      ),
    }));
  };

  // JSON Export / Import helpers
  const exportContentJson = () => {
    const jsonStr = JSON.stringify(content, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `resume_${resumeId}_content.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const importContentJson = (imported: ResumeContent) => {
    setContentState(imported);
  };

  const exportStyleJson = () => {
    const jsonStr = JSON.stringify(style, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `resume_${resumeId}_style.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const importStyleJson = (imported: ResumeStyle) => {
    setStyleState(imported);
  };

  return (
    <ResumeContext.Provider
      value={{
        resumeId,
        title,
        content,
        style,
        version,
        saveStatus,
        hasLocalResumes,
        lastSaved,
        zoom,
        activeTab,
        activeSectionId,
        loading,
        resolveConflict,
        importLocalResumes,
        setZoom,
        setActiveTab,
        setActiveSectionId,
        setTitle,
        updateContent,
        updateHeader,
        reorderSections,
        toggleSectionVisibility,
        toggleSectionPageBreak,
        removeSection,
        duplicateSection,
        addSection,
        updateSectionTitle,
        addItem,
        duplicateItem,
        removeItem,
        reorderItems,
        updateItem,
        addBullet,
        removeBullet,
        reorderBullets,
        updateBullet,
        canUndo,
        canRedo,
        undo,
        redo,
        startStyleDrag,
        endStyleDrag,
        onePageFitActive,
        onePageFitWarning,
        toggleOnePageFit,
        updateStyle,
        applyPreset,
        exportContentJson,
        importContentJson,
        exportStyleJson,
        importStyleJson,
        saveNow,
      }}
    >
      {children}
    </ResumeContext.Provider>
  );
};

export const useResume = () => {
  const ctx = useContext(ResumeContext);
  if (!ctx) {
    throw new Error('useResume must be used within a ResumeProvider');
  }
  return ctx;
};

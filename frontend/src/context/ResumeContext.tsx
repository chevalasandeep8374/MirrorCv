'use client';

import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { arrayMove } from '@dnd-kit/sortable';
import { ResumeContent, ResumeSection, SectionItem, SectionType, HeaderContent } from '@/types/content';
import { ResumeStyle } from '@/types/style';
import { Resume } from '@/types/resume';
import { apiClient } from '@/lib/api';
import { classicSingleColumnPreset, defaultResumeContent } from '@/lib/presets';

type SaveStatus = 'saved' | 'saving' | 'unsaved' | 'error';

interface ResumeContextType {
  resumeId: string;
  title: string;
  content: ResumeContent;
  style: ResumeStyle;
  saveStatus: SaveStatus;
  lastSaved: Date | null;
  zoom: number;
  activeTab: 'content' | 'style' | 'templates';
  activeSectionId: string | null;
  loading: boolean;

  // View / UI
  setZoom: (zoom: number | ((prev: number) => number)) => void;
  setActiveTab: (tab: 'content' | 'style' | 'templates') => void;
  setActiveSectionId: (id: string | null) => void;
  setTitle: (title: string) => void;

  // Content Actions
  updateContent: (content: ResumeContent) => void;
  updateHeader: (header: Partial<HeaderContent>) => void;
  reorderSections: (oldIndex: number, newIndex: number) => void;
  toggleSectionVisibility: (sectionId: string) => void;
  removeSection: (sectionId: string) => void;
  addSection: (type: SectionType, title?: string) => void;
  updateSectionTitle: (sectionId: string, title: string) => void;
  addItem: (sectionId: string) => void;
  removeItem: (sectionId: string, itemId: string) => void;
  reorderItems: (sectionId: string, oldIndex: number, newIndex: number) => void;
  updateItem: (sectionId: string, itemId: string, itemData: Partial<SectionItem>) => void;
  addBullet: (sectionId: string, itemId: string) => void;
  removeBullet: (sectionId: string, itemId: string, bulletId: string) => void;
  reorderBullets: (sectionId: string, itemId: string, oldIndex: number, newIndex: number) => void;
  updateBullet: (sectionId: string, itemId: string, bulletId: string, text: string) => void;

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
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('saved');
  const [lastSaved, setLastSaved] = useState<Date | null>(new Date());
  const [zoom, setZoom] = useState(1);
  const [activeTab, setActiveTab] = useState<'content' | 'style' | 'templates'>('content');
  const [activeSectionId, setActiveSectionId] = useState<string | null>(null);

  const isInitialMount = useRef(true);
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch resume if not provided as initial prop
  useEffect(() => {
    if (initialResume) return;

    async function fetchResume() {
      try {
        setLoading(true);
        const res = await apiClient.get<Resume>(`/resumes/${resumeId}`);
        setTitleState(res.data.title || 'Untitled Resume');
        setContentState(res.data.content || defaultResumeContent);
        setStyleState(res.data.style || classicSingleColumnPreset);
      } catch (err) {
        console.error('Failed to load resume:', err);
        setSaveStatus('error');
      } finally {
        setLoading(false);
      }
    }

    fetchResume();
  }, [resumeId, initialResume]);

  // Autosave execution function
  const executeSave = useCallback(
    async (curTitle: string, curContent: ResumeContent, curStyle: ResumeStyle) => {
      setSaveStatus('saving');
      try {
        await apiClient.put(`/resumes/${resumeId}`, {
          title: curTitle,
          content: curContent,
          style: curStyle,
        });
        setSaveStatus('saved');
        setLastSaved(new Date());
      } catch (err) {
        console.error('Autosave error:', err);
        setSaveStatus('error');
      }
    },
    [resumeId]
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
    setStyleState(preset);
  };

  // Header update
  const updateHeader = (patch: Partial<HeaderContent>) => {
    setContentState((prev) => ({
      ...prev,
      header: {
        ...prev.header,
        ...patch,
      },
    }));
  };

  // Section actions
  const reorderSections = (oldIndex: number, newIndex: number) => {
    setContentState((prev) => ({
      ...prev,
      sections: arrayMove(prev.sections, oldIndex, newIndex),
    }));
  };

  const toggleSectionVisibility = (sectionId: string) => {
    setContentState((prev) => ({
      ...prev,
      sections: prev.sections.map((s) =>
        s.id === sectionId ? { ...s, visible: !s.visible } : s
      ),
    }));
  };

  const removeSection = (sectionId: string) => {
    setContentState((prev) => ({
      ...prev,
      sections: prev.sections.filter((s) => s.id !== sectionId),
    }));
    if (activeSectionId === sectionId) setActiveSectionId(null);
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

    setContentState((prev) => ({
      ...prev,
      sections: [...prev.sections, newSection],
    }));
    setActiveSectionId(id);
  };

  const updateSectionTitle = (sectionId: string, newTitle: string) => {
    setContentState((prev) => ({
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

    setContentState((prev) => ({
      ...prev,
      sections: prev.sections.map((s) =>
        s.id === sectionId ? { ...s, items: [...(s.items || []), newItem] } : s
      ),
    }));
  };

  const removeItem = (sectionId: string, itemId: string) => {
    setContentState((prev) => ({
      ...prev,
      sections: prev.sections.map((s) =>
        s.id === sectionId
          ? { ...s, items: s.items.filter((item) => item.id !== itemId) }
          : s
      ),
    }));
  };

  const reorderItems = (sectionId: string, oldIndex: number, newIndex: number) => {
    setContentState((prev) => ({
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
    setContentState((prev) => ({
      ...prev,
      sections: prev.sections.map((s) =>
        s.id === sectionId
          ? {
              ...s,
              items: s.items.map((item) =>
                item.id === itemId ? { ...item, ...itemData } : item
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

    setContentState((prev) => ({
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
    setContentState((prev) => ({
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
    setContentState((prev) => ({
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
    text: string
  ) => {
    setContentState((prev) => ({
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
                        b.id === bulletId ? { ...b, text } : b
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
        saveStatus,
        lastSaved,
        zoom,
        activeTab,
        activeSectionId,
        loading,
        setZoom,
        setActiveTab,
        setActiveSectionId,
        setTitle,
        updateContent,
        updateHeader,
        reorderSections,
        toggleSectionVisibility,
        removeSection,
        addSection,
        updateSectionTitle,
        addItem,
        removeItem,
        reorderItems,
        updateItem,
        addBullet,
        removeBullet,
        reorderBullets,
        updateBullet,
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

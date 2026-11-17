'use client';

import React from 'react';
import { X, Command } from 'lucide-react';

interface KeyboardShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SHORTCUTS = [
  { keys: ['Ctrl', 'Z'], macKeys: ['⌘', 'Z'], description: 'Undo last content change' },
  { keys: ['Ctrl', 'Y'], macKeys: ['⌘', 'Shift', 'Z'], description: 'Redo last content change' },
  { keys: ['Ctrl', 'S'], macKeys: ['⌘', 'S'], description: 'Force save resume changes' },
  { keys: ['Ctrl', 'P'], macKeys: ['⌘', 'P'], description: 'Print or export PDF' },
  { keys: ['Ctrl', '1'], macKeys: ['⌘', '1'], description: 'Switch to Overview tab' },
  { keys: ['Ctrl', '2'], macKeys: ['⌘', '2'], description: 'Switch to Content tab' },
  { keys: ['Ctrl', '3'], macKeys: ['⌘', '3'], description: 'Switch to Customize tab' },
  { keys: ['Ctrl', '4'], macKeys: ['⌘', '4'], description: 'Switch to AI Tools tab' },
];

export const KeyboardShortcutsModal: React.FC<KeyboardShortcutsModalProps> = ({
  isOpen,
  onClose,
}) => {
  if (!isOpen) return null;

  const isMac = typeof window !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4 animate-in fade-in">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-200">
        <div className="flex items-center justify-between p-4 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-blue-50 text-blue-600 rounded-lg">
              <Command className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-sm text-slate-800">Keyboard Shortcuts</h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-4 space-y-2">
          {SHORTCUTS.map((s, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between py-2 border-b border-slate-100 last:border-b-0 text-xs"
            >
              <span className="text-slate-600 font-medium">{s.description}</span>
              <div className="flex items-center gap-1 font-mono">
                {(isMac ? s.macKeys : s.keys).map((k, kIdx) => (
                  <kbd
                    key={kIdx}
                    className="px-2 py-0.5 bg-slate-100 border border-slate-300 text-slate-700 rounded text-[11px] font-bold shadow-2xs"
                  >
                    {k}
                  </kbd>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="p-3 bg-slate-50 border-t border-slate-100 text-right">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-xl shadow-xs transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

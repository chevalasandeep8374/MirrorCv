'use client';

import React from 'react';
import { AlertTriangle, Lock, Unlock, X } from 'lucide-react';

interface DetachTemplateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirmDetach: () => void;
}

export const DetachTemplateModal: React.FC<DetachTemplateModalProps> = ({
  isOpen,
  onClose,
  onConfirmDetach,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-amber-50/50">
          <div className="flex items-center gap-2.5 text-amber-700">
            <div className="p-2 bg-amber-100 rounded-xl">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-base text-slate-900">Detach to Edit Design?</h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          <p className="text-sm text-slate-600 leading-relaxed">
            Your resume layout and geometry are currently locked to your uploaded Word (.docx) template to preserve <strong>exact byte-fidelity ECMA-376 composition</strong>.
          </p>

          <div className="bg-amber-50 rounded-xl p-3.5 border border-amber-200 text-xs text-amber-800 space-y-2">
            <div className="font-semibold flex items-center gap-1.5">
              <Unlock className="w-3.5 h-3.5" /> What happens when you detach:
            </div>
            <ul className="list-disc list-inside space-y-1 text-slate-700">
              <li>All design, typography, spacing, and column controls will be <strong>fully unlocked</strong>.</li>
              <li>Your extracted styling tokens will be preserved as a <strong>&quot;Custom (from your upload)&quot;</strong> design.</li>
              <li>A new editor-native copy of your resume will be created.</li>
              <li>Exact byte-fidelity DOCX export will no longer apply. Future downloads will use editor-native PDF and Simplified Word Export.</li>
            </ul>
          </div>

          <p className="text-xs text-slate-500">
            Your original uploaded template remains safely preserved in your account history.
          </p>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 bg-slate-50 border-t border-slate-100">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-200/70 rounded-xl transition-colors"
          >
            Keep Template Locked
          </button>
          <button
            type="button"
            onClick={() => {
              onConfirmDetach();
              onClose();
            }}
            className="px-4 py-2 text-xs font-bold text-white bg-amber-600 hover:bg-amber-700 rounded-xl shadow-xs transition-colors flex items-center gap-1.5"
          >
            <Unlock className="w-3.5 h-3.5" />
            Detach and Unlock Styling
          </button>
        </div>
      </div>
    </div>
  );
};

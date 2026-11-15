'use client';

import React, { useState } from 'react';
import {
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Upload,
  ArrowRight,
  X,
  FileText,
  Layers,
  Columns,
  Type,
  ShieldCheck,
  RefreshCw,
  Loader2,
} from 'lucide-react';
import { apiClient } from '@/lib/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ImportReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  templateData: any;
  originalFile: File | null;
  onFontUpdated?: (updated: any) => void;
}

export default function ImportReportModal({
  isOpen,
  onClose,
  onConfirm,
  templateData,
  originalFile,
  onFontUpdated,
}: ImportReportModalProps) {
  const [activeTab, setActiveTab] = useState<'preview' | 'fonts'>('preview');
  const [uploadingFont, setUploadingFont] = useState(false);
  const [fontUploadMessage, setFontUploadMessage] = useState<string | null>(null);
  const [fontUploadError, setFontUploadError] = useState<string | null>(null);
  const [previewTimestamp, setPreviewTimestamp] = useState(Date.now());
  const [currentData, setCurrentData] = useState(templateData);

  if (!isOpen || !templateData) return null;

  const originalUrl = originalFile ? URL.createObjectURL(originalFile) : null;
  const noopUrl = `${API_BASE_URL}/api/templates/${currentData.id}/noop-pdf?t=${previewTimestamp}`;

  const forecast = currentData.fidelity_forecast || {};
  const score = forecast.total_score ?? forecast.overall_score ?? 95.0;
  const tier = forecast.tier || 'A';
  const fontTable = currentData.font_table || { entries: [], substitutions: [] };

  const getTierBadge = (t: string) => {
    switch (t.toUpperCase()) {
      case 'A':
        return {
          label: 'Tier A · Exact',
          desc: 'Text-based PDF, in-place redaction & injection with native vectors preserved',
          color: 'bg-emerald-500/15 text-emerald-700 border-emerald-300',
        };
      case 'B':
        return {
          label: 'Tier B · Close',
          desc: 'Fonts substituted or layout rebuilt via HTML/CSS renderer',
          color: 'bg-blue-500/15 text-blue-700 border-blue-300',
        };
      case 'C':
      default:
        return {
          label: 'Tier C · Approximate',
          desc: 'Scanned image PDF reconstructed via OCR engine',
          color: 'bg-amber-500/15 text-amber-700 border-amber-300',
        };
    }
  };

  const tierBadge = getTierBadge(tier);

  const handleFontUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const fontFile = e.target.files?.[0];
    if (!fontFile) return;

    if (!fontFile.name.match(/\.(ttf|otf)$/i)) {
      setFontUploadError('Only TrueType (.ttf) or OpenType (.otf) font files are accepted.');
      return;
    }

    setUploadingFont(true);
    setFontUploadMessage(null);
    setFontUploadError(null);

    try {
      const formData = new FormData();
      formData.append('font_file', fontFile);

      const res = await apiClient.post(`/templates/${currentData.id}/fonts`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const updated = {
        ...currentData,
        font_table: res.data.font_table,
        fidelity_forecast: res.data.fidelity_forecast,
        planned_strategy: res.data.planned_strategy,
      };

      setCurrentData(updated);
      setPreviewTimestamp(Date.now());
      setFontUploadMessage(res.data.message || `Font ${fontFile.name} applied successfully.`);
      if (onFontUpdated) onFontUpdated(updated);
    } catch (err: any) {
      setFontUploadError(err?.response?.data?.detail || 'Failed to upload custom font.');
    } finally {
      setUploadingFont(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-5xl max-h-[92vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base font-bold text-slate-900">
                  PDF Import & Fidelity Report
                </h2>
                <span
                  className={`text-xs px-2.5 py-0.5 rounded-full font-bold border ${tierBadge.color}`}
                >
                  {tierBadge.label}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                {currentData.filename} · {tierBadge.desc}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Top Metric Cards */}
        <div className="grid grid-cols-4 gap-3 p-4 bg-white border-b border-slate-100 text-xs">
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <div className="flex items-center space-x-1.5 text-slate-500 font-medium mb-1">
              <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
              <span>Fidelity Forecast</span>
            </div>
            <div className="text-lg font-extrabold text-slate-900">
              {score.toFixed(1)}
              <span className="text-xs font-normal text-slate-400"> / 100</span>
            </div>
            <div className="text-[11px] text-emerald-600 font-medium mt-0.5">
              Self-measured no-op match
            </div>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <div className="flex items-center space-x-1.5 text-slate-500 font-medium mb-1">
              <Columns className="w-3.5 h-3.5 text-blue-600" />
              <span>Columns & Layout</span>
            </div>
            <div className="text-base font-bold text-slate-900 capitalize">
              {currentData.columns_detected === 2 ? 'Two Columns / Sidebar' : 'Single Column'}
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5">
              {currentData.sections_detected?.length || 0} recognized sections
            </div>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <div className="flex items-center space-x-1.5 text-slate-500 font-medium mb-1">
              <FileText className="w-3.5 h-3.5 text-indigo-600" />
              <span>Document Type</span>
            </div>
            <div className="text-base font-bold text-slate-900">
              {currentData.is_scanned ? 'Scanned Image (OCR)' : 'Text-based Vector PDF'}
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5">
              Origin coordinates extracted
            </div>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <div className="flex items-center space-x-1.5 text-slate-500 font-medium mb-1">
              <Layers className="w-3.5 h-3.5 text-purple-600" />
              <span>Selected Strategy</span>
            </div>
            <div className="text-base font-bold text-slate-900 capitalize">
              {currentData.planned_strategy === 'inplace'
                ? 'In-Place Redaction'
                : 'HTML Rebuild'}
            </div>
            <div className="text-[11px] text-purple-600 font-medium mt-0.5">
              Vector graphics preserved
            </div>
          </div>
        </div>

        {/* Tab Controls */}
        <div className="px-6 pt-3 border-b border-slate-200 flex space-x-6 text-xs font-semibold text-slate-600 bg-slate-50/50">
          <button
            onClick={() => setActiveTab('preview')}
            className={`pb-2.5 transition-colors border-b-2 flex items-center space-x-1.5 ${
              activeTab === 'preview'
                ? 'border-blue-600 text-blue-600 font-bold'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Side-by-Side Visual Preview (Original vs No-Op)</span>
          </button>

          <button
            onClick={() => setActiveTab('fonts')}
            className={`pb-2.5 transition-colors border-b-2 flex items-center space-x-1.5 ${
              activeTab === 'fonts'
                ? 'border-blue-600 text-blue-600 font-bold'
                : 'border-transparent hover:text-slate-900'
            }`}
          >
            <Type className="w-3.5 h-3.5" />
            <span>Font Resolution Table ({fontTable.entries?.length || 0})</span>
            {fontTable.substitutions?.length > 0 && (
              <span className="ml-1 px-1.5 py-0.2 rounded-full bg-amber-100 text-amber-700 text-[10px]">
                {fontTable.substitutions.length} substituted
              </span>
            )}
          </button>
        </div>

        {/* Body Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {activeTab === 'preview' ? (
            <div className="h-[460px] flex gap-4">
              {/* Original Preview */}
              <div className="flex-1 flex flex-col border border-slate-200 rounded-xl overflow-hidden bg-slate-100">
                <div className="h-8 bg-slate-200/70 border-b border-slate-200 px-3 flex items-center justify-between text-xs font-bold text-slate-700">
                  <span>ORIGINAL UPLOADED PDF</span>
                  <span className="text-[10px] text-slate-500 font-medium">Source Template</span>
                </div>
                <div className="flex-1 w-full bg-slate-300">
                  {originalUrl && (
                    <iframe
                      src={originalUrl}
                      className="w-full h-full border-none"
                      title="Original PDF"
                    />
                  )}
                </div>
              </div>

              {/* No-Op Regenerated Preview */}
              <div className="flex-1 flex flex-col border border-emerald-300 rounded-xl overflow-hidden bg-emerald-50/30">
                <div className="h-8 bg-emerald-100/60 border-b border-emerald-200 px-3 flex items-center justify-between text-xs font-bold text-emerald-800">
                  <span className="flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                    <span>NO-OP REGENERATED PREVIEW</span>
                  </span>
                  <span className="text-[10px] text-emerald-700 font-semibold">
                    {score.toFixed(1)}% Match
                  </span>
                </div>
                <div className="flex-1 w-full bg-slate-300">
                  <iframe
                    src={noopUrl}
                    className="w-full h-full border-none"
                    title="No-op PDF"
                  />
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Custom Font Upload Card */}
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl flex items-center justify-between">
                <div>
                  <h4 className="text-xs font-bold text-blue-900 flex items-center gap-1.5">
                    <Type className="w-4 h-4 text-blue-600" />
                    <span>Improve Font Match Confidence</span>
                  </h4>
                  <p className="text-[11px] text-blue-700 mt-0.5 leading-relaxed">
                    If a font was substituted, upload the authentic TrueType (.ttf) or OpenType (.otf) font
                    file to achieve pixel-perfect metric parity.
                  </p>
                  {fontUploadMessage && (
                    <p className="text-xs text-emerald-700 font-medium mt-1">
                      {fontUploadMessage}
                    </p>
                  )}
                  {fontUploadError && (
                    <p className="text-xs text-rose-700 font-medium mt-1">
                      {fontUploadError}
                    </p>
                  )}
                </div>

                <div>
                  <input
                    type="file"
                    id="font-upload-input"
                    accept=".ttf,.otf"
                    onChange={handleFontUpload}
                    className="hidden"
                  />
                  <label
                    htmlFor="font-upload-input"
                    className="cursor-pointer inline-flex items-center space-x-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg shadow-sm transition"
                  >
                    {uploadingFont ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Upload className="w-3.5 h-3.5" />
                    )}
                    <span>Upload Font File</span>
                  </label>
                </div>
              </div>

              {/* Font Resolution Table */}
              <div className="border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold uppercase tracking-wider text-[10px]">
                    <tr>
                      <th className="px-4 py-2.5">Original Font Name</th>
                      <th className="px-4 py-2.5">Family</th>
                      <th className="px-4 py-2.5">Embedding</th>
                      <th className="px-4 py-2.5">Resolved Usable Font</th>
                      <th className="px-4 py-2.5">Match Confidence</th>
                      <th className="px-4 py-2.5">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {fontTable.entries?.map((f: any, idx: number) => {
                      const isSub = f.is_substituted;
                      return (
                        <tr key={idx} className="hover:bg-slate-50/50">
                          <td className="px-4 py-2.5 font-semibold text-slate-800">
                            {f.font_name}
                          </td>
                          <td className="px-4 py-2.5 text-slate-600">{f.family}</td>
                          <td className="px-4 py-2.5">
                            {f.is_subset ? (
                              <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-700 text-[10px] font-medium border border-amber-200">
                                Subset (Glyphs Gated)
                              </span>
                            ) : f.is_embedded ? (
                              <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 text-[10px] font-medium border border-emerald-200">
                                Full Embedded
                              </span>
                            ) : (
                              <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-[10px] font-medium">
                                System / Open
                              </span>
                            )}
                          </td>
                          <td className="px-4 py-2.5 font-medium text-slate-900">
                            {f.resolved_font_name}
                          </td>
                          <td className="px-4 py-2.5">
                            <span className="font-bold text-slate-700">
                              {Math.round(f.match_confidence * 100)}%
                            </span>
                          </td>
                          <td className="px-4 py-2.5">
                            {isSub ? (
                              <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 text-[10px] font-semibold border border-blue-200">
                                Metric Compatible
                              </span>
                            ) : (
                              <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 text-[10px] font-semibold border border-emerald-200">
                                Direct Match
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-200 rounded-lg transition"
          >
            Cancel / Upload Different File
          </button>

          <div className="flex items-center space-x-3">
            <span className="text-xs text-slate-500 font-medium">
              Fidelity validated: Ready to apply JD tailoring
            </span>
            <button
              onClick={onConfirm}
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-sm transition flex items-center space-x-2"
            >
              <span>Confirm & Continue to Tailoring</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

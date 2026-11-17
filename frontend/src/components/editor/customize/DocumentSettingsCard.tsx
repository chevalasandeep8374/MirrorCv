'use client';

import React from 'react';
import { useResume } from '@/context/ResumeContext';
import { Globe, Calendar, FileText } from 'lucide-react';
import { SUPPORTED_LOCALES, SupportedLocale, getLocaleDirection } from '@/lib/i18n';
import { formatStructuredDate } from '@/lib/migration';

const DATE_FORMATS = [
  { id: 'MMM YYYY', label: 'Month Year (e.g. May 2024)' },
  { id: 'MM/YYYY', label: 'Numeric (e.g. 05/2024)' },
  { id: 'MMMM YYYY', label: 'Full Month (e.g. May 2024)' },
  { id: 'YYYY', label: 'Year Only (e.g. 2024)' },
];

export const DocumentSettingsCard: React.FC = () => {
  const { style, updateStyle } = useResume();

  const currentLocale = (style.locale || 'en') as SupportedLocale;
  const currentDateFormat = style.dateFormat || 'MMM YYYY';
  const currentPageSize = style.pageSize || 'A4';

  const handleLocaleChange = (newLocale: SupportedLocale) => {
    const dir = getLocaleDirection(newLocale);
    updateStyle({
      ...style,
      locale: newLocale,
      direction: dir,
    });
  };

  const handleDateFormatChange = (newFormat: string) => {
    updateStyle({
      ...style,
      dateFormat: newFormat,
    });
  };

  const handlePageSizeChange = (newPageSize: 'A4' | 'Letter') => {
    updateStyle({
      ...style,
      pageSize: newPageSize,
    });
  };

  // Live date preview using current month & year
  const now = new Date();
  const sampleDateStr = formatStructuredDate(
    {
      startMonth: now.getMonth() + 1,
      startYear: now.getFullYear(),
      endMonth: null,
      endYear: null,
      isCurrent: true,
    },
    currentDateFormat
  );

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-5">
      <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
        <div className="p-2 bg-blue-50 text-blue-600 rounded-xl">
          <Globe className="w-4 h-4" />
        </div>
        <div>
          <h3 className="font-bold text-sm text-slate-900">Document Settings</h3>
          <p className="text-xs text-slate-500">Language, date conventions, and page sizing</p>
        </div>
      </div>

      {/* 1. Language */}
      <div className="space-y-2">
        <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
          <Globe className="w-3.5 h-3.5 text-slate-400" /> Document Language
        </label>
        <select
          id="document-language-select"
          aria-label="Document Language"
          value={currentLocale}
          onChange={(e) => handleLocaleChange(e.target.value as SupportedLocale)}
          className="w-full text-xs font-medium px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-hidden"
        >
          {Object.entries(SUPPORTED_LOCALES).map(([code, info]) => (
            <option key={code} value={code}>
              {info.name} ({info.nativeName})
            </option>
          ))}
        </select>
        <p className="text-[11px] text-slate-400">
          Switches section heading translations and text direction (LTR / RTL).
        </p>
      </div>

      {/* 2. Date Format */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-slate-400" /> Date Format
          </label>
          <span className="text-[11px] font-mono text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md font-semibold">
            {sampleDateStr}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2">
          {DATE_FORMATS.map((fmt) => (
            <button
              key={fmt.id}
              type="button"
              onClick={() => handleDateFormatChange(fmt.id)}
              className={`px-3 py-2 rounded-xl text-left border text-xs font-medium transition-all ${
                currentDateFormat === fmt.id
                  ? 'border-blue-600 bg-blue-50/50 text-blue-700 font-semibold shadow-xs'
                  : 'border-slate-200 hover:border-slate-300 text-slate-700'
              }`}
            >
              {fmt.id}
            </button>
          ))}
        </div>
      </div>

      {/* 3. Page Size */}
      <div className="space-y-2">
        <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
          <FileText className="w-3.5 h-3.5 text-slate-400" /> Page Format
        </label>
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => handlePageSizeChange('A4')}
            className={`px-3 py-2.5 rounded-xl border text-center text-xs font-medium transition-all ${
              currentPageSize === 'A4'
                ? 'border-blue-600 bg-blue-50/50 text-blue-700 font-bold shadow-xs'
                : 'border-slate-200 hover:border-slate-300 text-slate-700'
            }`}
          >
            <div>A4</div>
            <div className="text-[10px] text-slate-400 font-normal">210 × 297 mm (Global)</div>
          </button>
          <button
            type="button"
            onClick={() => handlePageSizeChange('Letter')}
            className={`px-3 py-2.5 rounded-xl border text-center text-xs font-medium transition-all ${
              currentPageSize === 'Letter'
                ? 'border-blue-600 bg-blue-50/50 text-blue-700 font-bold shadow-xs'
                : 'border-slate-200 hover:border-slate-300 text-slate-700'
            }`}
          >
            <div>US Letter</div>
            <div className="text-[10px] text-slate-400 font-normal">8.5 × 11 in (North America)</div>
          </button>
        </div>
      </div>
    </div>
  );
};

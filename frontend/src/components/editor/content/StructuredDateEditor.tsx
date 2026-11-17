'use client';

import React, { useState } from 'react';
import { StructuredDates } from '@/types/content';
import { formatStructuredDate } from '@/lib/migration';
import { Calendar, ToggleLeft, ToggleRight, Check } from 'lucide-react';

interface StructuredDateEditorProps {
  dates?: StructuredDates | null;
  dateRange: string;
  dateFormat?: string;
  onChange: (dates: StructuredDates | null, dateRange: string) => void;
}

const MONTHS = [
  { value: 1, label: '01 - Jan' },
  { value: 2, label: '02 - Feb' },
  { value: 3, label: '03 - Mar' },
  { value: 4, label: '04 - Apr' },
  { value: 5, label: '05 - May' },
  { value: 6, label: '06 - Jun' },
  { value: 7, label: '07 - Jul' },
  { value: 8, label: '08 - Aug' },
  { value: 9, label: '09 - Sep' },
  { value: 10, label: '10 - Oct' },
  { value: 11, label: '11 - Nov' },
  { value: 12, label: '12 - Dec' },
];

export const StructuredDateEditor: React.FC<StructuredDateEditorProps> = ({
  dates,
  dateRange,
  dateFormat = 'MMM YYYY',
  onChange,
}) => {
  // If dates object exists with at least one field, prefer structured mode
  const hasStructured = Boolean(
    dates &&
      (dates.startYear != null ||
        dates.startMonth != null ||
        dates.endYear != null ||
        dates.endMonth != null ||
        dates.isCurrent)
  );

  const [isStructuredMode, setIsStructuredMode] = useState<boolean>(hasStructured || !dateRange);

  const currentDates: StructuredDates = dates || {
    startMonth: null,
    startYear: null,
    endMonth: null,
    endYear: null,
    isCurrent: false,
  };

  const updateStructured = (patch: Partial<StructuredDates>) => {
    const nextDates: StructuredDates = {
      ...currentDates,
      ...patch,
    };
    const formatted = formatStructuredDate(nextDates, dateFormat);
    onChange(nextDates, formatted);
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-[11px] font-semibold text-slate-500">
        <span className="flex items-center gap-1.5">
          <Calendar className="w-3.5 h-3.5 text-blue-600" />
          <span>Dates / Timeframe</span>
        </span>

        <button
          type="button"
          onClick={() => {
            const nextMode = !isStructuredMode;
            setIsStructuredMode(nextMode);
            if (!nextMode && !dateRange && dates) {
              onChange(dates, formatStructuredDate(dates, dateFormat));
            }
          }}
          className="text-[10px] text-blue-600 hover:text-blue-700 flex items-center gap-1 font-medium transition-colors"
        >
          {isStructuredMode ? (
            <>
              <ToggleRight className="w-4 h-4 text-blue-600" />
              <span>Structured Pickers</span>
            </>
          ) : (
            <>
              <ToggleLeft className="w-4 h-4 text-slate-400" />
              <span>Freeform Text</span>
            </>
          )}
        </button>
      </div>

      {isStructuredMode ? (
        <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-xl space-y-2 text-xs">
          {/* Start Date */}
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-[10px] font-bold text-slate-500 mb-0.5">Start Month</label>
              <select
                value={currentDates.startMonth ?? ''}
                onChange={(e) =>
                  updateStructured({
                    startMonth: e.target.value ? parseInt(e.target.value, 10) : null,
                  })
                }
                className="w-full text-xs px-2 py-1 bg-white border border-slate-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
              >
                <option value="">Month (opt)</option>
                {MONTHS.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[10px] font-bold text-slate-500 mb-0.5">Start Year</label>
              <input
                type="number"
                placeholder="e.g. 2021"
                min={1950}
                max={2099}
                value={currentDates.startYear ?? ''}
                onChange={(e) =>
                  updateStructured({
                    startYear: e.target.value ? parseInt(e.target.value, 10) : null,
                  })
                }
                className="w-full text-xs px-2 py-1 bg-white border border-slate-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* End Date / Present */}
          <div className="grid grid-cols-2 gap-2 items-end">
            <div>
              <label className="block text-[10px] font-bold text-slate-500 mb-0.5">End Month</label>
              <select
                disabled={currentDates.isCurrent}
                value={currentDates.isCurrent ? '' : (currentDates.endMonth ?? '')}
                onChange={(e) =>
                  updateStructured({
                    endMonth: e.target.value ? parseInt(e.target.value, 10) : null,
                  })
                }
                className="w-full text-xs px-2 py-1 bg-white border border-slate-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 disabled:opacity-40 disabled:bg-slate-100"
              >
                <option value="">Month (opt)</option>
                {MONTHS.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[10px] font-bold text-slate-500 mb-0.5">End Year</label>
              <input
                type="number"
                placeholder="e.g. 2024"
                min={1950}
                max={2099}
                disabled={currentDates.isCurrent}
                value={currentDates.isCurrent ? '' : (currentDates.endYear ?? '')}
                onChange={(e) =>
                  updateStructured({
                    endYear: e.target.value ? parseInt(e.target.value, 10) : null,
                  })
                }
                className="w-full text-xs px-2 py-1 bg-white border border-slate-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 disabled:opacity-40 disabled:bg-slate-100"
              />
            </div>
          </div>

          {/* Present Checkbox & Live Preview */}
          <div className="flex items-center justify-between pt-1 border-t border-slate-200/60">
            <label className="flex items-center gap-1.5 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={Boolean(currentDates.isCurrent)}
                onChange={(e) => updateStructured({ isCurrent: e.target.checked })}
                className="w-3.5 h-3.5 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
              />
              <span className="text-[11px] font-semibold text-slate-700">Currently working / Present</span>
            </label>

            {dateRange && (
              <span className="text-[10px] font-mono text-slate-500 bg-slate-200/70 px-1.5 py-0.5 rounded">
                Preview: {dateRange}
              </span>
            )}
          </div>
        </div>
      ) : (
        <input
          type="text"
          value={dateRange}
          onChange={(e) => onChange(dates ?? null, e.target.value)}
          placeholder="e.g. 2021 – Present or Jan 2020 – Dec 2023"
          className="w-full text-xs px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 bg-white"
        />
      )}
    </div>
  );
};

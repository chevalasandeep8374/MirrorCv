'use client';

import React from 'react';
import { useResume } from '@/context/ResumeContext';
import { User, AlignCenter, AlignLeft, Image as ImageIcon } from 'lucide-react';
import { HeaderConfig, PhotoConfig } from '@/types/style';

export const HeaderPhotoCard: React.FC = () => {
  const { style, content, updateStyle } = useResume();

  const headerConfig = style.header || {
    alignment: 'left',
    arrangement: 'bullet',
  };

  const photoConfig = style.photo || {
    shape: 'circle',
    size: 'medium',
    border: 'thin',
    position: 'right',
  };

  const hasPhoto = Boolean(content.header.photoUrl || style.decorations?.avatarUrl);

  const handleHeaderUpdate = (patch: Partial<HeaderConfig>) => {
    updateStyle({
      ...style,
      header: {
        ...headerConfig,
        ...patch,
      },
    });
  };

  const handlePhotoUpdate = (patch: Partial<PhotoConfig>) => {
    updateStyle({
      ...style,
      photo: {
        ...photoConfig,
        ...patch,
      },
    });
  };

  const handleToggleBanner = (enabled: boolean) => {
    updateStyle({
      ...style,
      decorations: {
        ...style.decorations,
        headerBanner: enabled,
      },
      layout: {
        ...style.layout,
        type: enabled ? 'header_banner' : style.layout.type === 'header_banner' ? 'single' : style.layout.type,
      },
    });
  };

  const isBanner = style.layout.type === 'header_banner' || Boolean(style.decorations?.headerBanner);

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs space-y-5">
      <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
        <div className="p-2 bg-teal-50 text-teal-600 rounded-xl">
          <User className="w-4 h-4" />
        </div>
        <div>
          <h3 className="font-bold text-sm text-slate-900">Header & Photo</h3>
          <p className="text-xs text-slate-500">Alignment, details separators, banner, and photo framing</p>
        </div>
      </div>

      {/* 1. Header Alignment */}
      <div className="space-y-2">
        <label className="text-xs font-semibold text-slate-700">Header Text Alignment</label>
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => handleHeaderUpdate({ alignment: 'left' })}
            className={`p-3 rounded-xl border flex items-center gap-2 text-xs font-medium transition-all ${
              headerConfig.alignment !== 'center'
                ? 'border-teal-600 bg-teal-50/50 text-teal-900 font-bold shadow-xs'
                : 'border-slate-200 hover:border-slate-300 text-slate-700'
            }`}
          >
            <AlignLeft className="w-4 h-4" />
            <span>Left Aligned</span>
          </button>
          <button
            type="button"
            onClick={() => handleHeaderUpdate({ alignment: 'center' })}
            className={`p-3 rounded-xl border flex items-center gap-2 text-xs font-medium transition-all ${
              headerConfig.alignment === 'center'
                ? 'border-teal-600 bg-teal-50/50 text-teal-900 font-bold shadow-xs'
                : 'border-slate-200 hover:border-slate-300 text-slate-700'
            }`}
          >
            <AlignCenter className="w-4 h-4" />
            <span>Center Aligned</span>
          </button>
        </div>
      </div>

      {/* 2. Contact Details Separator */}
      <div className="space-y-2">
        <label className="text-xs font-semibold text-slate-700">Contact Details Separator</label>
        <div className="grid grid-cols-3 gap-2">
          {[
            { id: 'bullet', label: 'Bullet (•)' },
            { id: 'pipe', label: 'Pipe (|)' },
            { id: 'bar', label: 'Slash (/)' },
          ].map((sep) => (
            <button
              key={sep.id}
              type="button"
              onClick={() => handleHeaderUpdate({ arrangement: sep.id as any })}
              className={`py-2 px-2.5 rounded-xl border text-center text-xs font-medium transition-all ${
                headerConfig.arrangement === sep.id
                  ? 'border-teal-600 bg-teal-50/50 text-teal-900 font-bold shadow-xs'
                  : 'border-slate-200 hover:border-slate-300 text-slate-700'
              }`}
            >
              {sep.label}
            </button>
          ))}
        </div>
      </div>

      {/* 3. Header Banner Style */}
      <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
        <div>
          <div className="text-xs font-semibold text-slate-800">Header Banner Background</div>
          <div className="text-[11px] text-slate-500">Wraps header in high-contrast solid dark banner</div>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            aria-label="Header Banner Background"
            checked={isBanner}
            onChange={(e) => handleToggleBanner(e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-slate-200 peer-focus:outline-hidden rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-teal-600"></div>
        </label>
      </div>

      {/* 4. Profile Photo Controls (if photo is uploaded) */}
      {hasPhoto && (
        <div className="space-y-3 pt-3 border-t border-slate-100">
          <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
            <ImageIcon className="w-3.5 h-3.5 text-slate-400" /> Photo Framing & Size
          </label>

          {/* Shape */}
          <div className="space-y-1">
            <span className="text-[11px] text-slate-500">Avatar Shape</span>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'circle', label: 'Circle' },
                { id: 'rounded', label: 'Rounded' },
                { id: 'square', label: 'Square' },
              ].map((s) => (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => handlePhotoUpdate({ shape: s.id as any })}
                  className={`py-1.5 rounded-xl border text-center text-xs font-medium transition-all ${
                    photoConfig.shape === s.id
                      ? 'border-teal-600 bg-teal-50/50 text-teal-900 font-bold shadow-xs'
                      : 'border-slate-200 text-slate-700'
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          {/* Size */}
          <div className="space-y-1">
            <span className="text-[11px] text-slate-500">Avatar Size</span>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'small', label: 'Small (64px)' },
                { id: 'medium', label: 'Medium (80px)' },
                { id: 'large', label: 'Large (96px)' },
              ].map((sz) => (
                <button
                  key={sz.id}
                  type="button"
                  onClick={() => handlePhotoUpdate({ size: sz.id as any })}
                  className={`py-1.5 rounded-xl border text-center text-xs font-medium transition-all ${
                    photoConfig.size === sz.id
                      ? 'border-teal-600 bg-teal-50/50 text-teal-900 font-bold shadow-xs'
                      : 'border-slate-200 text-slate-700'
                  }`}
                >
                  {sz.label}
                </button>
              ))}
            </div>
          </div>

          {/* Border */}
          <div className="space-y-1">
            <span className="text-[11px] text-slate-500">Photo Border</span>
            <div className="grid grid-cols-4 gap-1.5">
              {[
                { id: 'none', label: 'None' },
                { id: 'thin', label: 'Thin' },
                { id: 'thick', label: 'Thick' },
                { id: 'accent', label: 'Accent' },
              ].map((b) => (
                <button
                  key={b.id}
                  type="button"
                  onClick={() => handlePhotoUpdate({ border: b.id as any })}
                  className={`py-1.5 rounded-xl border text-center text-[11px] font-medium transition-all ${
                    photoConfig.border === b.id
                      ? 'border-teal-600 bg-teal-50/50 text-teal-900 font-bold shadow-xs'
                      : 'border-slate-200 text-slate-700'
                  }`}
                >
                  {b.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

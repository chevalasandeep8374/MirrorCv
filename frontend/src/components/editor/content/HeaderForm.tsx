'use client';

import React, { useRef } from 'react';
import { useResume } from '@/context/ResumeContext';
import { FieldVisibility, ContactLink } from '@/types/content';
import {
  Plus,
  Trash2,
  Link as LinkIcon,
  User,
  Camera,
  Eye,
  EyeOff,
  ChevronDown,
  Mail,
  Phone,
  MapPin,
  Globe,
  SlidersHorizontal,
} from 'lucide-react';

const LINK_PRESETS = [
  { label: 'LinkedIn', urlPrefix: 'https://linkedin.com/in/' },
  { label: 'GitHub', urlPrefix: 'https://github.com/' },
  { label: 'Portfolio', urlPrefix: 'https://' },
  { label: 'Twitter / X', urlPrefix: 'https://x.com/' },
  { label: 'Website', urlPrefix: 'https://' },
];

interface HeaderFormProps {
  isExpanded?: boolean;
  onToggleExpand?: () => void;
}

export const HeaderForm: React.FC<HeaderFormProps> = ({
  isExpanded: externalExpanded,
  onToggleExpand,
}) => {
  const [internalExpanded, setInternalExpanded] = React.useState(true);
  const isExpanded = externalExpanded !== undefined ? externalExpanded : internalExpanded;
  const toggleExpand = onToggleExpand || (() => setInternalExpanded((prev) => !prev));

  const { content, style, updateHeader, updateStyle } = useResume();
  const header = content.header;
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fieldVisibility = header.fieldVisibility || {
    name: true,
    title: true,
    email: true,
    phone: true,
    location: true,
    website: true,
    photo: true,
  };

  const isVisible = (field: keyof FieldVisibility): boolean => {
    return fieldVisibility[field] !== false;
  };

  const toggleFieldVisibility = (field: keyof FieldVisibility) => {
    const current = isVisible(field);
    updateHeader({
      fieldVisibility: {
        ...fieldVisibility,
        [field]: !current,
      },
    });
  };

  const handleLinkChange = (id: string, field: 'label' | 'url', val: string) => {
    const updatedLinks = (header.links || []).map((link) =>
      link.id === id ? { ...link, [field]: val } : link
    );
    updateHeader({ links: updatedLinks });
  };

  const handleAddLink = (preset?: { label: string; urlPrefix: string }) => {
    const newLink: ContactLink = {
      id: `link-${Date.now()}`,
      label: preset?.label || 'LinkedIn',
      url: preset?.urlPrefix || 'https://linkedin.com/in/',
    };
    updateHeader({ links: [...(header.links || []), newLink] });
  };

  const handleRemoveLink = (id: string) => {
    updateHeader({ links: (header.links || []).filter((l) => l.id !== id) });
  };

  // Photo Upload Handler with Client-Side 300x300 Square Crop Canvas
  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      alert('Only JPEG, PNG, and WebP images are allowed.');
      e.target.value = '';
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      alert('Photo must be smaller than 5MB.');
      e.target.value = '';
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const size = Math.min(img.width, img.height);
        canvas.width = 300;
        canvas.height = 300;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          const offsetX = (img.width - size) / 2;
          const offsetY = (img.height - size) / 2;
          ctx.drawImage(img, offsetX, offsetY, size, size, 0, 0, 300, 300);
          const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
          updateHeader({
            photoUrl: dataUrl,
            fieldVisibility: {
              ...fieldVisibility,
              photo: true,
            },
          });
          updateStyle({
            ...style,
            photo: {
              ...style.photo,
              shape: style.photo?.shape || 'circle',
              border: style.photo?.border || 'thin',
              size: style.photo?.size || 'medium',
            },
            decorations: {
              ...style.decorations,
              showAvatar: true,
              avatarShape: style.decorations?.avatarShape || 'circle',
            },
          });
        }
      };
      img.src = event.target?.result as string;
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  const handleRemovePhoto = () => {
    updateHeader({
      photoUrl: undefined,
      fieldVisibility: {
        ...fieldVisibility,
        photo: false,
      },
    });
    updateStyle({
      ...style,
      decorations: {
        ...style.decorations,
        showAvatar: false,
      },
    });
  };

  const photoShape = style.photo?.shape || (style.decorations?.avatarShape === 'square' ? 'square' : 'circle');
  const showPhoto = isVisible('photo') && Boolean(header.photoUrl);

  const setPhotoShape = (shape: 'circle' | 'square' | 'off') => {
    if (shape === 'off') {
      updateStyle({
        ...style,
        decorations: {
          ...style.decorations,
          showAvatar: false,
        },
      });
      toggleFieldVisibility('photo');
    } else {
      updateStyle({
        ...style,
        photo: {
          ...style.photo,
          shape: shape === 'square' ? 'square' : 'circle',
        },
        decorations: {
          ...style.decorations,
          avatarShape: shape === 'square' ? 'square' : 'circle',
          showAvatar: true,
        },
      });
      if (!isVisible('photo')) {
        toggleFieldVisibility('photo');
      }
    }
  };

  // Compute initials fallback
  const initials = header.name
    ? header.name
        .split(' ')
        .filter(Boolean)
        .map((n) => n[0])
        .join('')
        .slice(0, 2)
        .toUpperCase()
    : 'AM';

  return (
    <div
      className={`bg-white rounded-xl border mb-3.5 overflow-hidden transition-all duration-300 ${
        isExpanded
          ? 'border-slate-300 shadow-md ring-2 ring-slate-900/5'
          : 'border-slate-200/90 hover:border-slate-300 shadow-xs hover:shadow-sm hover:-translate-y-0.5 cursor-pointer'
      }`}
    >
      {/* Stage Summary Trigger Header */}
      <div
        onClick={toggleExpand}
        className="p-3.5 sm:p-4 flex items-center justify-between cursor-pointer select-none hover:bg-slate-50/70 transition-colors duration-150 group"
      >
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-slate-800 shrink-0 transition-colors duration-200 group-hover:bg-slate-200/80">
            <User className="w-4 h-4" />
          </div>
          <div className="min-w-0 leading-tight">
            <div className="flex items-center gap-2">
              <span className="font-bold text-[15px] sm:text-[16px] text-slate-900 tracking-tight group-hover:text-blue-900 transition-colors">
                Personal Details
              </span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" title="Active section" />
            </div>
            <span className="text-xs text-slate-400 block truncate mt-0.5">
              {header.name || 'Alex Mercer'} · {header.title || 'Senior Staff Software Engineer'}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1.5 shrink-0" onClick={(e) => e.stopPropagation()}>
          <button
            type="button"
            onClick={toggleExpand}
            className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition-all duration-150 cursor-pointer active:scale-95"
            title="Customize Section"
          >
            <SlidersHorizontal className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={() => toggleFieldVisibility('name')}
            className={`p-1.5 rounded-lg transition-all duration-150 cursor-pointer active:scale-95 ${
              isVisible('name')
                ? 'opacity-0 group-hover:opacity-100 text-slate-400 hover:text-slate-800 hover:bg-slate-100'
                : 'text-amber-500 bg-amber-50 hover:bg-amber-100'
            }`}
            title="Toggle visibility in preview"
          >
            {isVisible('name') ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
          </button>
          <button
            type="button"
            onClick={toggleExpand}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-800 transition-all duration-150 cursor-pointer active:scale-95"
          >
            <ChevronDown
              className={`w-4 h-4 transition-transform duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] ${
                isExpanded ? 'rotate-180' : ''
              }`}
            />
          </button>
        </div>
      </div>

      {/* Smooth Animated Content */}
      <div
        className={`grid transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] ${
          isExpanded ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0 pointer-events-none'
        }`}
      >
        <div className="min-h-0 overflow-hidden">
          <div className="px-4 pb-4 pt-2 border-t border-slate-100 space-y-3">
          {/* Avatar / Photo Upload Row */}
          <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50/80 border border-slate-200">
            <div className="flex items-center gap-3">
              <div
                className={`relative w-11 h-11 bg-slate-200 border border-white shadow-xs overflow-hidden flex items-center justify-center text-slate-800 font-bold text-sm shrink-0 ${
                  photoShape === 'circle' ? 'rounded-full' : 'rounded-lg'
                }`}
              >
                {header.photoUrl && showPhoto ? (
                  /* eslint-disable-next-line @next/next/no-img-element */
                  <img
                    src={header.photoUrl}
                    alt={header.name || 'Profile'}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span>{initials}</span>
                )}
              </div>
              <div>
                <span className="text-xs font-semibold text-slate-800 block">Profile Photo</span>
                <span className="text-[11px] text-slate-400 block">Optional for single-column A4</span>
              </div>
            </div>

            <div className="flex items-center gap-1.5">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handlePhotoUpload}
                className="hidden"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="px-2.5 py-1 bg-white border border-slate-200 rounded-md text-[11px] font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-2xs cursor-pointer"
              >
                {header.photoUrl ? 'Change' : 'Upload'}
              </button>
              {header.photoUrl && (
                <button
                  type="button"
                  onClick={handleRemovePhoto}
                  className="text-[11px] text-rose-600 hover:underline font-medium px-1 cursor-pointer"
                >
                  Remove
                </button>
              )}
              <div className="flex items-center bg-white p-0.5 rounded-md border border-slate-200 ml-1">
                <button
                  type="button"
                  onClick={() => setPhotoShape('circle')}
                  className={`px-2 py-0.5 text-[11px] font-medium rounded transition-colors ${
                    showPhoto && photoShape === 'circle'
                      ? 'bg-slate-100 font-bold text-slate-900 shadow-2xs'
                      : 'text-slate-400 hover:text-slate-700'
                  }`}
                >
                  Circle
                </button>
                <button
                  type="button"
                  onClick={() => setPhotoShape('square')}
                  className={`px-2 py-0.5 text-[11px] font-medium rounded transition-colors ${
                    showPhoto && photoShape === 'square'
                      ? 'bg-slate-100 font-bold text-slate-900 shadow-2xs'
                      : 'text-slate-400 hover:text-slate-700'
                  }`}
                >
                  Square
                </button>
                <button
                  type="button"
                  onClick={() => setPhotoShape('off')}
                  className={`px-2 py-0.5 text-[11px] font-medium rounded transition-colors ${
                    !showPhoto
                      ? 'bg-slate-100 font-bold text-slate-900 shadow-2xs'
                      : 'text-slate-400 hover:text-slate-700'
                  }`}
                >
                  Off
                </button>
              </div>
            </div>
          </div>

          {/* Full Name & Professional Headline */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-[11px] font-semibold text-slate-700">Full Name</label>
                <button
                  type="button"
                  onClick={() => toggleFieldVisibility('name')}
                  className={`p-0.5 rounded transition-colors ${
                    isVisible('name') ? 'text-slate-500 hover:text-slate-800' : 'text-slate-300'
                  }`}
                  title={isVisible('name') ? 'Visible on resume' : 'Hidden on resume'}
                >
                  {isVisible('name') ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                </button>
              </div>
              <input
                type="text"
                value={header.name || ''}
                onChange={(e) => updateHeader({ name: e.target.value })}
                placeholder="Alex Mercer"
                className={`w-full px-3 py-2 rounded-md border text-xs transition-all ${
                  isVisible('name')
                    ? 'bg-slate-50/70 border-slate-200 text-slate-900 focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#181824]'
                    : 'bg-slate-100 border-slate-200 text-slate-400'
                }`}
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-[11px] font-semibold text-slate-700">Professional Headline</label>
                <button
                  type="button"
                  onClick={() => toggleFieldVisibility('title')}
                  className={`p-0.5 rounded transition-colors ${
                    isVisible('title') ? 'text-slate-500 hover:text-slate-800' : 'text-slate-300'
                  }`}
                  title={isVisible('title') ? 'Visible on resume' : 'Hidden on resume'}
                >
                  {isVisible('title') ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                </button>
              </div>
              <input
                type="text"
                value={header.title || ''}
                onChange={(e) => updateHeader({ title: e.target.value })}
                placeholder="Staff AI Systems & Agentic Architect"
                className={`w-full px-3 py-2 rounded-md border text-xs transition-all ${
                  isVisible('title')
                    ? 'bg-slate-50/70 border-slate-200 text-slate-900 focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#181824]'
                    : 'bg-slate-100 border-slate-200 text-slate-400'
                }`}
              />
            </div>
          </div>

          {/* Email Address & Phone Number */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-[11px] font-semibold text-slate-700">Email Address</label>
                <button
                  type="button"
                  onClick={() => toggleFieldVisibility('email')}
                  className={`p-0.5 rounded transition-colors ${
                    isVisible('email') ? 'text-slate-500 hover:text-slate-800' : 'text-slate-300'
                  }`}
                  title={isVisible('email') ? 'Visible on resume' : 'Hidden on resume'}
                >
                  {isVisible('email') ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                </button>
              </div>
              <div className="relative">
                <Mail className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="email"
                  value={header.email || ''}
                  onChange={(e) => updateHeader({ email: e.target.value })}
                  placeholder="alex.mercer@gmail.com"
                  className={`w-full pl-8 pr-2.5 py-2 rounded-md border text-xs transition-all ${
                    isVisible('email')
                      ? 'bg-slate-50/70 border-slate-200 text-slate-900 focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#181824]'
                      : 'bg-slate-100 border-slate-200 text-slate-400'
                  }`}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-[11px] font-semibold text-slate-700">Phone Number</label>
                <button
                  type="button"
                  onClick={() => toggleFieldVisibility('phone')}
                  className={`p-0.5 rounded transition-colors ${
                    isVisible('phone') ? 'text-slate-500 hover:text-slate-800' : 'text-slate-300'
                  }`}
                  title={isVisible('phone') ? 'Visible on resume' : 'Hidden on resume'}
                >
                  {isVisible('phone') ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                </button>
              </div>
              <div className="relative">
                <Phone className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="tel"
                  value={header.phone || ''}
                  onChange={(e) => updateHeader({ phone: e.target.value })}
                  placeholder="+1 (415) 890-4321"
                  className={`w-full pl-8 pr-2.5 py-2 rounded-md border text-xs transition-all ${
                    isVisible('phone')
                      ? 'bg-slate-50/70 border-slate-200 text-slate-900 focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#181824]'
                      : 'bg-slate-100 border-slate-200 text-slate-400'
                  }`}
                />
              </div>
            </div>
          </div>

          {/* Location & Portfolio / Website */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-[11px] font-semibold text-slate-700">Location</label>
                <button
                  type="button"
                  onClick={() => toggleFieldVisibility('location')}
                  className={`p-0.5 rounded transition-colors ${
                    isVisible('location') ? 'text-slate-500 hover:text-slate-800' : 'text-slate-300'
                  }`}
                  title={isVisible('location') ? 'Visible on resume' : 'Hidden on resume'}
                >
                  {isVisible('location') ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                </button>
              </div>
              <div className="relative">
                <MapPin className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="text"
                  value={header.location || ''}
                  onChange={(e) => updateHeader({ location: e.target.value })}
                  placeholder="San Francisco, CA (Open to Remote)"
                  className={`w-full pl-8 pr-2.5 py-2 rounded-md border text-xs transition-all ${
                    isVisible('location')
                      ? 'bg-slate-50/70 border-slate-200 text-slate-900 focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#181824]'
                      : 'bg-slate-100 border-slate-200 text-slate-400'
                  }`}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-[11px] font-semibold text-slate-700">Portfolio / Website</label>
                <button
                  type="button"
                  onClick={() => toggleFieldVisibility('website')}
                  className={`p-0.5 rounded transition-colors ${
                    isVisible('website') ? 'text-slate-500 hover:text-slate-800' : 'text-slate-300'
                  }`}
                  title={isVisible('website') ? 'Visible on resume' : 'Hidden on resume'}
                >
                  {isVisible('website') ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                </button>
              </div>
              <div className="relative">
                <Globe className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="text"
                  value={header.website || ''}
                  onChange={(e) => updateHeader({ website: e.target.value })}
                  placeholder="alexmercer.dev"
                  className={`w-full pl-8 pr-2.5 py-2 rounded-md border text-xs transition-all ${
                    isVisible('website')
                      ? 'bg-slate-50/70 border-slate-200 text-slate-900 focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#181824]'
                      : 'bg-slate-100 border-slate-200 text-slate-400'
                  }`}
                />
              </div>
            </div>
          </div>

          {/* Social Profiles & Preset Pills */}
          <div className="pt-2 border-t border-slate-100 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-slate-700">Social Profiles</span>
              <span className="text-[10px] font-mono text-slate-400">Quick presets</span>
            </div>

            {/* Quick Preset Pills */}
            <div className="flex flex-wrap items-center gap-1.5">
              {LINK_PRESETS.map((preset) => (
                <button
                  key={preset.label}
                  type="button"
                  onClick={() => handleAddLink(preset)}
                  className="px-2 py-0.5 text-[11px] font-medium rounded-md bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors cursor-pointer"
                >
                  + {preset.label}
                </button>
              ))}
            </div>

            {/* List of links */}
            <div className="space-y-2 pt-1">
              {(header.links || []).map((link) => (
                <div key={link.id} className="flex items-center gap-2">
                  <input
                    type="text"
                    value={link.label}
                    onChange={(e) => handleLinkChange(link.id, 'label', e.target.value)}
                    placeholder="Label (e.g. GitHub)"
                    className="w-28 text-xs px-2.5 py-1.5 border border-slate-200 rounded-md bg-white focus:outline-none focus:ring-1 focus:ring-[#181824]"
                  />
                  <input
                    type="text"
                    value={link.url}
                    onChange={(e) => handleLinkChange(link.id, 'url', e.target.value)}
                    placeholder="https://..."
                    className="flex-1 text-xs px-2.5 py-1.5 border border-slate-200 rounded-md bg-white focus:outline-none focus:ring-1 focus:ring-[#181824]"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveLink(link.id)}
                    className="p-1 text-slate-400 hover:text-rose-600 transition-colors cursor-pointer"
                    title="Remove link"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);
};

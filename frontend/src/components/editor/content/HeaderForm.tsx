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
  Circle,
  Square,
  Sparkles,
} from 'lucide-react';

const LINK_PRESETS = [
  { label: 'LinkedIn', urlPrefix: 'https://linkedin.com/in/' },
  { label: 'GitHub', urlPrefix: 'https://github.com/' },
  { label: 'Portfolio', urlPrefix: 'https://' },
  { label: 'Twitter / X', urlPrefix: 'https://x.com/' },
  { label: 'Website', urlPrefix: 'https://' },
];

export const HeaderForm: React.FC = () => {
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
    const updatedLinks = header.links.map((link) =>
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
    updateHeader({ links: header.links.filter((l) => l.id !== id) });
  };

  // Photo Upload Handler with Client-Side 400x400 Square Crop Canvas
  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Security: Validate image MIME type and file size (max 5MB)
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
          // Update photo style tokens
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

  const setPhotoShape = (shape: 'circle' | 'square' | 'rounded') => {
    updateStyle({
      ...style,
      photo: {
        ...style.photo,
        shape,
      },
      decorations: {
        ...style.decorations,
        avatarShape: shape === 'square' ? 'square' : 'circle',
        showAvatar: true,
      },
    });
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs mb-4 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100 text-slate-800">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-blue-50 text-blue-600 rounded-lg">
            <User className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-sm">Personal & Contact Details</h3>
            <p className="text-[11px] text-slate-400">Toggle eye icons to show or hide fields on your resume</p>
          </div>
        </div>
      </div>

      {/* Photo Upload Section */}
      <div className="flex items-center gap-4 p-3 bg-slate-50 border border-slate-200 rounded-xl">
        <div className="relative shrink-0">
          {header.photoUrl ? (
            /* eslint-disable-next-line @next/next/no-img-element */
            <img
              src={header.photoUrl}
              alt={header.name || 'Profile'}
              className={`w-14 h-14 object-cover border-2 border-white shadow-xs ${
                photoShape === 'circle' ? 'rounded-full' : photoShape === 'rounded' ? 'rounded-xl' : 'rounded-md'
              } ${!showPhoto ? 'opacity-40 grayscale' : ''}`}
            />
          ) : (
            <div
              className={`w-14 h-14 bg-slate-200 border-2 border-white shadow-xs flex items-center justify-center text-slate-400 ${
                photoShape === 'circle' ? 'rounded-full' : photoShape === 'rounded' ? 'rounded-xl' : 'rounded-md'
              }`}
            >
              <Camera className="w-6 h-6" />
            </div>
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <span className="font-bold text-xs text-slate-800">Profile Photo</span>
            {header.photoUrl && (
              <div className="flex items-center space-x-1">
                <button
                  type="button"
                  onClick={() => setPhotoShape('circle')}
                  className={`p-1 rounded ${
                    photoShape === 'circle'
                      ? 'bg-blue-100 text-blue-600'
                      : 'text-slate-400 hover:text-slate-600'
                  }`}
                  title="Circle Shape"
                >
                  <Circle className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={() => setPhotoShape('square')}
                  className={`p-1 rounded ${
                    photoShape === 'square'
                      ? 'bg-blue-100 text-blue-600'
                      : 'text-slate-400 hover:text-slate-600'
                  }`}
                  title="Square Shape"
                >
                  <Square className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={() => toggleFieldVisibility('photo')}
                  className={`p-1 rounded transition-colors ${
                    showPhoto ? 'text-blue-600' : 'text-slate-400'
                  }`}
                  title={showPhoto ? 'Hide Photo on Resume' : 'Show Photo on Resume'}
                >
                  {showPhoto ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
                </button>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-2 mt-1.5">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handlePhotoUpload}
              className="hidden"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="px-2.5 py-1 bg-white border border-slate-300 rounded text-[11px] font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-2xs"
            >
              {header.photoUrl ? 'Change Photo' : 'Upload Photo'}
            </button>
            {header.photoUrl && (
              <button
                type="button"
                onClick={handleRemovePhoto}
                className="text-[11px] text-rose-600 hover:underline font-medium"
              >
                Remove
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Inputs with Field-Level Visibility Toggles */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Full Name */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-[11px] font-semibold text-slate-600">Full Name</label>
            <button
              type="button"
              onClick={() => toggleFieldVisibility('name')}
              className={`p-0.5 rounded transition-colors ${
                isVisible('name') ? 'text-blue-600' : 'text-slate-300 hover:text-slate-500'
              }`}
              title={isVisible('name') ? 'Shown on resume' : 'Hidden on resume'}
            >
              {isVisible('name') ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
            </button>
          </div>
          <input
            type="text"
            value={header.name || ''}
            onChange={(e) => updateHeader({ name: e.target.value })}
            placeholder="Alex Mercer"
            className={`w-full text-xs px-3 py-2 border rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 transition-colors ${
              isVisible('name') ? 'border-slate-200 bg-white' : 'border-slate-200 bg-slate-50 text-slate-400'
            }`}
          />
        </div>

        {/* Title / Headline */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-[11px] font-semibold text-slate-600">Professional Headline</label>
            <button
              type="button"
              onClick={() => toggleFieldVisibility('title')}
              className={`p-0.5 rounded transition-colors ${
                isVisible('title') ? 'text-blue-600' : 'text-slate-300 hover:text-slate-500'
              }`}
              title={isVisible('title') ? 'Shown on resume' : 'Hidden on resume'}
            >
              {isVisible('title') ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
            </button>
          </div>
          <input
            type="text"
            value={header.title || ''}
            onChange={(e) => updateHeader({ title: e.target.value })}
            placeholder="Principal Staff Software Engineer"
            className={`w-full text-xs px-3 py-2 border rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 transition-colors ${
              isVisible('title') ? 'border-slate-200 bg-white' : 'border-slate-200 bg-slate-50 text-slate-400'
            }`}
          />
        </div>

        {/* Email */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-[11px] font-semibold text-slate-600">Email Address</label>
            <button
              type="button"
              onClick={() => toggleFieldVisibility('email')}
              className={`p-0.5 rounded transition-colors ${
                isVisible('email') ? 'text-blue-600' : 'text-slate-300 hover:text-slate-500'
              }`}
              title={isVisible('email') ? 'Shown on resume' : 'Hidden on resume'}
            >
              {isVisible('email') ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
            </button>
          </div>
          <input
            type="email"
            value={header.email || ''}
            onChange={(e) => updateHeader({ email: e.target.value })}
            placeholder="alex.mercer@example.com"
            className={`w-full text-xs px-3 py-2 border rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 transition-colors ${
              isVisible('email') ? 'border-slate-200 bg-white' : 'border-slate-200 bg-slate-50 text-slate-400'
            }`}
          />
        </div>

        {/* Phone */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-[11px] font-semibold text-slate-600">Phone Number</label>
            <button
              type="button"
              onClick={() => toggleFieldVisibility('phone')}
              className={`p-0.5 rounded transition-colors ${
                isVisible('phone') ? 'text-blue-600' : 'text-slate-300 hover:text-slate-500'
              }`}
              title={isVisible('phone') ? 'Shown on resume' : 'Hidden on resume'}
            >
              {isVisible('phone') ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
            </button>
          </div>
          <input
            type="text"
            value={header.phone || ''}
            onChange={(e) => updateHeader({ phone: e.target.value })}
            placeholder="+1 (555) 019-2834"
            className={`w-full text-xs px-3 py-2 border rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 transition-colors ${
              isVisible('phone') ? 'border-slate-200 bg-white' : 'border-slate-200 bg-slate-50 text-slate-400'
            }`}
          />
        </div>

        {/* Location */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-[11px] font-semibold text-slate-600">Location</label>
            <button
              type="button"
              onClick={() => toggleFieldVisibility('location')}
              className={`p-0.5 rounded transition-colors ${
                isVisible('location') ? 'text-blue-600' : 'text-slate-300 hover:text-slate-500'
              }`}
              title={isVisible('location') ? 'Shown on resume' : 'Hidden on resume'}
            >
              {isVisible('location') ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
            </button>
          </div>
          <input
            type="text"
            value={header.location || ''}
            onChange={(e) => updateHeader({ location: e.target.value })}
            placeholder="San Francisco, CA"
            className={`w-full text-xs px-3 py-2 border rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 transition-colors ${
              isVisible('location') ? 'border-slate-200 bg-white' : 'border-slate-200 bg-slate-50 text-slate-400'
            }`}
          />
        </div>

        {/* Website */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-[11px] font-semibold text-slate-600">Portfolio / Website</label>
            <button
              type="button"
              onClick={() => toggleFieldVisibility('website')}
              className={`p-0.5 rounded transition-colors ${
                isVisible('website') ? 'text-blue-600' : 'text-slate-300 hover:text-slate-500'
              }`}
              title={isVisible('website') ? 'Shown on resume' : 'Hidden on resume'}
            >
              {isVisible('website') ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
            </button>
          </div>
          <input
            type="text"
            value={header.website || ''}
            onChange={(e) => updateHeader({ website: e.target.value })}
            placeholder="https://alexmercer.dev"
            className={`w-full text-xs px-3 py-2 border rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 transition-colors ${
              isVisible('website') ? 'border-slate-200 bg-white' : 'border-slate-200 bg-slate-50 text-slate-400'
            }`}
          />
        </div>
      </div>

      {/* Social / Portfolio Links */}
      <div className="pt-3 border-t border-slate-100 space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
            <LinkIcon className="w-3.5 h-3.5 text-blue-600" />
            <span>Social & Professional Links</span>
          </label>
          <div className="flex items-center gap-1">
            {LINK_PRESETS.map((preset) => (
              <button
                key={preset.label}
                type="button"
                onClick={() => handleAddLink(preset)}
                className="px-2 py-0.5 text-[10px] font-semibold bg-slate-100 hover:bg-blue-50 hover:text-blue-600 text-slate-600 rounded transition-colors"
              >
                + {preset.label}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          {header.links?.map((link) => (
            <div key={link.id} className="flex items-center space-x-2">
              <input
                type="text"
                value={link.label}
                onChange={(e) => handleLinkChange(link.id, 'label', e.target.value)}
                placeholder="Label (e.g. GitHub)"
                className="w-1/3 text-xs px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 bg-white"
              />
              <input
                type="text"
                value={link.url}
                onChange={(e) => handleLinkChange(link.id, 'url', e.target.value)}
                placeholder="https://..."
                className="flex-1 text-xs px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 bg-white"
              />
              <button
                type="button"
                onClick={() => handleRemoveLink(link.id)}
                className="p-1 text-slate-400 hover:text-rose-500 transition-colors"
                title="Remove link"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

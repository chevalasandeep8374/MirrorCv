'use client';

import React, { useRef } from 'react';
import { useResume } from '@/context/ResumeContext';
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
} from 'lucide-react';

export const HeaderForm: React.FC = () => {
  const { content, style, updateHeader, updateStyle } = useResume();
  const header = content.header;
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleLinkChange = (id: string, field: 'label' | 'url', val: string) => {
    const updatedLinks = header.links.map((link) =>
      link.id === id ? { ...link, [field]: val } : link
    );
    updateHeader({ links: updatedLinks });
  };

  const handleAddLink = () => {
    const newLink = {
      id: `link-${Date.now()}`,
      label: 'LinkedIn',
      url: 'https://linkedin.com/in/',
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
          updateHeader({ photoUrl: dataUrl });
          // Enable avatar visibility in style
          updateStyle({
            ...style,
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
    updateHeader({ photoUrl: undefined });
    updateStyle({
      ...style,
      decorations: {
        ...style.decorations,
        showAvatar: false,
      },
    });
  };

  const toggleAvatarShape = (shape: 'circle' | 'square') => {
    updateStyle({
      ...style,
      decorations: {
        ...style.decorations,
        avatarShape: shape,
        showAvatar: true,
      },
    });
  };

  const toggleAvatarVisibility = () => {
    const current = style.decorations?.showAvatar ?? Boolean(header.photoUrl);
    updateStyle({
      ...style,
      decorations: {
        ...style.decorations,
        showAvatar: !current,
      },
    });
  };

  const showAvatar = style.decorations?.showAvatar ?? Boolean(header.photoUrl);
  const avatarShape = style.decorations?.avatarShape || 'circle';

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm mb-4">
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100 text-slate-800">
        <div className="flex items-center space-x-2">
          <User className="w-4 h-4 text-blue-600" />
          <h3 className="font-bold text-sm">Personal & Contact Info</h3>
        </div>
      </div>

      {/* Photo Upload Section */}
      <div className="flex items-center gap-4 mb-4 p-3 bg-slate-50 border border-slate-200 rounded-xl">
        <div className="relative shrink-0">
          {header.photoUrl ? (
            /* eslint-disable-next-line @next/next/no-img-element */
            <img
              src={header.photoUrl}
              alt={header.name || 'Profile'}
              className={`w-14 h-14 object-cover border-2 border-white shadow-sm ${
                avatarShape === 'circle' ? 'rounded-full' : 'rounded-lg'
              }`}
            />
          ) : (
            <div
              className={`w-14 h-14 bg-slate-200 border-2 border-white shadow-sm flex items-center justify-center text-slate-400 ${
                avatarShape === 'circle' ? 'rounded-full' : 'rounded-lg'
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
                  onClick={() => toggleAvatarShape('circle')}
                  className={`p-1 rounded ${
                    avatarShape === 'circle'
                      ? 'bg-blue-100 text-blue-600'
                      : 'text-slate-400 hover:text-slate-600'
                  }`}
                  title="Circle Shape"
                >
                  <Circle className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={() => toggleAvatarShape('square')}
                  className={`p-1 rounded ${
                    avatarShape === 'square'
                      ? 'bg-blue-100 text-blue-600'
                      : 'text-slate-400 hover:text-slate-600'
                  }`}
                  title="Square Shape"
                >
                  <Square className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={toggleAvatarVisibility}
                  className={`p-1 rounded ${
                    showAvatar ? 'text-blue-600' : 'text-slate-400'
                  }`}
                  title={showAvatar ? 'Hide Photo on Resume' : 'Show Photo on Resume'}
                >
                  {showAvatar ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1">
            Full Name
          </label>
          <input
            type="text"
            value={header.name || ''}
            onChange={(e) => updateHeader({ name: e.target.value })}
            placeholder="Alex Mercer"
            className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1">
            Professional Title / Headline
          </label>
          <input
            type="text"
            value={header.title || ''}
            onChange={(e) => updateHeader({ title: e.target.value })}
            placeholder="Senior Staff Software Engineer"
            className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1">
            Email Address
          </label>
          <input
            type="email"
            value={header.email || ''}
            onChange={(e) => updateHeader({ email: e.target.value })}
            placeholder="alex.mercer@example.com"
            className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1">
            Phone Number
          </label>
          <input
            type="text"
            value={header.phone || ''}
            onChange={(e) => updateHeader({ phone: e.target.value })}
            placeholder="+1 (555) 019-2834"
            className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1">
            Location
          </label>
          <input
            type="text"
            value={header.location || ''}
            onChange={(e) => updateHeader({ location: e.target.value })}
            placeholder="San Francisco, CA"
            className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1">
            Portfolio / Website URL
          </label>
          <input
            type="text"
            value={header.website || ''}
            onChange={(e) => updateHeader({ website: e.target.value })}
            placeholder="https://alexmercer.dev"
            className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Social / Portfolio Links */}
      <div className="mt-4 pt-3 border-t border-slate-100">
        <div className="flex items-center justify-between mb-2">
          <label className="text-xs font-semibold text-slate-600 flex items-center gap-1.5">
            <LinkIcon className="w-3.5 h-3.5 text-slate-400" />
            <span>Social & Professional Links</span>
          </label>
          <button
            type="button"
            onClick={handleAddLink}
            className="text-xs text-blue-600 hover:text-blue-700 font-semibold inline-flex items-center gap-1"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Link</span>
          </button>
        </div>

        <div className="space-y-2">
          {header.links?.map((link) => (
            <div key={link.id} className="flex items-center space-x-2">
              <input
                type="text"
                value={link.label}
                onChange={(e) => handleLinkChange(link.id, 'label', e.target.value)}
                placeholder="Label (e.g. GitHub)"
                className="w-1/3 text-xs px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              <input
                type="text"
                value={link.url}
                onChange={(e) => handleLinkChange(link.id, 'url', e.target.value)}
                placeholder="https://..."
                className="flex-1 text-xs px-2.5 py-1.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              <button
                type="button"
                onClick={() => handleRemoveLink(link.id)}
                className="p-1 text-slate-400 hover:text-rose-500 transition-colors"
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

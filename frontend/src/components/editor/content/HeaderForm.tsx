'use client';

import React from 'react';
import { useResume } from '@/context/ResumeContext';
import { Plus, Trash2, Link as LinkIcon, User } from 'lucide-react';

export const HeaderForm: React.FC = () => {
  const { content, updateHeader } = useResume();
  const header = content.header;

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

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm mb-4">
      <div className="flex items-center space-x-2 pb-3 mb-3 border-b border-slate-100 text-slate-800">
        <User className="w-4 h-4 text-blue-600" />
        <h3 className="font-bold text-sm">Personal & Contact Info</h3>
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

'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowLeft, Sparkles, Check, FileCheck, Layers, Cpu, ShieldCheck } from 'lucide-react';

export default function ChangelogPage() {
  const releases = [
    {
      id: 'flowcv-editor-v2',
      version: 'v2.4.0',
      date: 'November 2026',
      badge: 'Current Release',
      title: 'FlowCV-Class Editor Engine with Sub-Millimeter Parity',
      description: 'Major upgrade to the in-browser resume editor delivering a unified 4-tab navigation shell (Content, Customize, AI Tools, Overview), structured month/year dates, field-level eye toggles, and verified font rendering across 15 self-hosted open typography families.',
      highlights: [
        'Unified 4-tab editor layout with full undo/redo state synchronization and dirty state tracking.',
        'Structured Month/Year date formatters with "Current" status toggle and seamless fallback to freeform dateRange.',
        'Per-section and per-entry eye toggles to hide sensitive or secondary items from the preview, PDF, and scoring without losing data.',
        '15 self-hosted typography families loaded locally with zero external Google Fonts CDN network calls.',
        'TaskFlow visual language integration with tokenized glass system (.glass-1, .glass-2, .glass-3) and tactile 3D bevel actions.'
      ]
    },
    {
      id: 'adversarial-verifier',
      version: 'v2.3.0',
      date: 'October 2026',
      badge: 'Core Engine',
      title: 'Adversarial Bullet Verifier & Grounded Job Tailoring',
      description: 'Introduced an adversarial verification pipeline that intercepts every AI bullet suggestion. If a generated bullet introduces hallucinated revenue metrics, exaggerated team counts, or unverified skills, the verifier automatically rejects the edit.',
      highlights: [
        'Deterministic fact-checking against the candidate’s verified master profile history.',
        'Full visual diff view requiring explicit user confirmation before applying bullet revisions.',
        'Target qualification gap scanner highlighting essential skills missing from the target job description.'
      ]
    },
    {
      id: 'docx-preservation',
      version: 'v2.2.0',
      date: 'September 2026',
      badge: 'File Fidelity',
      title: 'Byte-Level DOCX Template Preservation',
      description: 'Engineered an OpenXML tokenizer that injects tailored content directly into existing Microsoft Word files without mutating original fonts, margins, tab stops, or bullet indentation geometries.',
      highlights: [
        'Byte-exact template preservation for existing executive and corporate Word resumes.',
        'Support for complex tables, header banners, and multi-column sidebar Word layouts.',
        'Instant side-by-side XML integrity validator.'
      ]
    },
    {
      id: 'vector-parity',
      version: 'v2.1.0',
      date: 'August 2026',
      badge: 'Parity Standard',
      title: 'Sub-Point Print & Headless PDF Parity Engine',
      description: 'Replaced browser printing with a synchronized headless Chromium vector rendering pipeline, ensuring the on-screen canvas and downloaded PDF match within 0.65 pt coordinate tolerance.',
      highlights: [
        'Automated 28-combination visual regression baseline suite.',
        'Orphan-prevention layout constraints eliminating awkward bullet point breaks.',
        'Zero font substitution guarantees across all supported platforms.'
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-page text-slate-900 font-sans selection:bg-primary/10 selection:text-primary flex flex-col">
      {/* Top Header */}
      <header className="sticky top-0 z-50 glass-1 h-16 px-6 md:px-12 flex items-center justify-between border-b border-border-subtle">
        <div className="w-full max-w-5xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 group">
            <span className="font-heading font-extrabold text-2xl tracking-tight text-slate-950">
              MirrorCV
            </span>
            <span className="w-2 h-2 rounded-full bg-primary inline-block" />
          </Link>

          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-950 px-3 py-1.5 rounded-md hover:bg-slate-100 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Home</span>
          </Link>
        </div>
      </header>

      {/* Hero Header */}
      <div className="py-16 md:py-24 border-b border-border-subtle bg-slate-50/50" style={{ background: 'var(--ambient-hero)' }}>
        <div className="max-w-4xl mx-auto px-6 text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-50 text-pill-purple border border-purple-200 text-xs font-bold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Product Changelog</span>
          </div>
          <h1 className="font-heading font-extrabold text-4xl sm:text-5xl text-slate-950 tracking-tight">
            Engineered with verifiable precision.
          </h1>
          <p className="text-base text-slate-600 max-w-xl mx-auto">
            A chronological record of releases, performance improvements, and layout parity updates.
          </p>
        </div>
      </div>

      {/* Changelog Timeline */}
      <main className="max-w-4xl mx-auto px-6 py-16 w-full space-y-16">
        {releases.map((release) => (
          <article
            key={release.id}
            id={release.id}
            className="bg-white rounded-card border border-slate-200 p-8 shadow-sm space-y-6 scroll-mt-24"
          >
            {/* Release Header */}
            <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <span className="font-heading font-extrabold text-xl text-slate-950">
                  {release.version}
                </span>
                <span className="text-xs font-bold uppercase px-2.5 py-0.5 rounded-full bg-blue-50 text-primary border border-blue-200">
                  {release.badge}
                </span>
              </div>
              <time className="text-xs font-semibold text-slate-500">
                {release.date}
              </time>
            </div>

            {/* Release Content */}
            <div className="space-y-3">
              <h2 className="font-heading font-extrabold text-2xl text-slate-900 tracking-tight">
                {release.title}
              </h2>
              <p className="text-sm text-slate-600 leading-relaxed">
                {release.description}
              </p>
            </div>

            {/* Highlights List */}
            <div className="bg-slate-50 rounded-lg p-5 border border-slate-100 space-y-2.5">
              <div className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Key Improvements
              </div>
              <ul className="space-y-2">
                {release.highlights.map((hl, idx) => (
                  <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-700 leading-snug">
                    <Check className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    <span>{hl}</span>
                  </li>
                ))}
              </ul>
            </div>
          </article>
        ))}
      </main>

      {/* Simple Footer */}
      <footer className="border-t border-slate-200 bg-white py-12 px-6 text-center text-xs text-slate-500">
        <div>&copy; {new Date().getFullYear()} MirrorCV. Built for career precision.</div>
      </footer>
    </div>
  );
}

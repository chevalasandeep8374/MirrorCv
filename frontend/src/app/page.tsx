'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  FileText,
  Sliders,
  Sparkles,
  Layers,
  ArrowUpRight,
  Eye,
  Lock,
  Zap,
} from 'lucide-react';

export default function EditorialLandingPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-paper text-ink font-sans selection:bg-accent/15 selection:text-ink flex flex-col">
      {/* 1. Top Editorial Header */}
      <header className="sticky top-0 z-50 bg-paper/90 backdrop-blur-md border-b border-paper-border px-6 md:px-16 py-5 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <span className="font-editorial-headline text-2xl tracking-tighter text-ink">
            MirrorCV
          </span>
          <span className="w-2 h-2 rounded-full bg-accent inline-block"></span>
        </Link>

        {/* Center Editorial Links */}
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-ink-body">
          <a href="#editorial-craft" className="hover:text-ink transition-colors">
            Craft & Principles
          </a>
          <a href="#vector-parity" className="hover:text-ink transition-colors">
            Vector Parity
          </a>
          <Link href="/templates" className="hover:text-ink transition-colors">
            Templates
          </Link>
          <Link href="/tailor" className="hover:text-ink transition-colors">
            Tailor (DOCX)
          </Link>
        </nav>

        {/* Right CTA */}
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="btn-secondary !text-xs !py-2 !px-4"
          >
            Dashboard
          </Link>
          <Link
            href="/dashboard"
            className="btn-primary !text-xs !py-2 !px-5"
          >
            <span>Create Resume</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </header>

      {/* 2. Hero Section */}
      <section className="relative px-6 md:px-16 pt-16 md:pt-28 pb-30 md:pb-35 max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
        {/* Left Copy Column */}
        <div className="lg:col-span-6 space-y-6 md:space-y-8">
          {/* Subtle Pill Tag */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-pill bg-paper-surface border border-paper-border text-xs font-semibold text-ink-body">
            <span className="w-1.5 h-1.5 rounded-full bg-accent" />
            <span>Strict Separation of Content & Style</span>
          </div>

          {/* Confident Hero Headline */}
          <h1 className="hero-headline">
            Resumes engineered with editorial poise.
          </h1>

          {/* Body Copy */}
          <p className="font-editorial-body text-base md:text-[18px] max-w-xl">
            A calm, precision workspace built for candidates who care about proportion,
            sub-point font metrics, and verified vector PDF parity. No template lock-in. No hallucinated claims.
          </p>

          {/* Action Row */}
          <div className="flex flex-wrap items-center gap-4 pt-2">
            <Link
              href="/dashboard"
              className="btn-primary !text-base !py-3.5 !px-8 shadow-sm"
            >
              <span>Compose Your Resume</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/templates"
              className="btn-secondary !text-base !py-3.5 !px-7"
            >
              <span>Explore Gallery</span>
            </Link>
          </div>

          {/* Micro Proof Points */}
          <div className="pt-4 border-t border-paper-border/80 flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-ink-muted">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-accent" />
              <span>15 self-hosted open fonts</span>
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-accent" />
              <span>&le; 0.65 pt PDF word delta</span>
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-accent" />
              <span>100% private local storage</span>
            </span>
          </div>
        </div>

        {/* Right Floating Product Preview Column */}
        <div className="lg:col-span-6 relative flex justify-center">
          {/* Floating Callout 1 (Top-Right) */}
          <div className="absolute -top-4 right-2 sm:right-6 z-20 bg-paper-surface border border-paper-border rounded-pill px-3.5 py-1.5 text-xs font-semibold text-ink shadow-sm flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-accent" />
            <span>1:1 Vector PDF Parity</span>
          </div>

          {/* Floating Callout 2 (Bottom-Left) */}
          <div className="absolute -bottom-5 left-0 sm:left-4 z-20 bg-paper-surface border border-paper-border rounded-pill px-3.5 py-1.5 text-xs font-semibold text-ink shadow-sm flex items-center gap-2">
            <ShieldCheck className="w-3.5 h-3.5 text-accent" />
            <span>Zero Font Substitution</span>
          </div>

          {/* The Real Floating Product Preview */}
          <div className="w-full max-w-[500px] bg-white rounded-card border border-paper-border shadow-preview overflow-hidden transition-transform duration-300 hover:scale-[1.01]">
            <div className="grid grid-cols-12 min-h-[580px]">
              {/* Deep Navy Sidebar (~#1F3347) */}
              <div className="col-span-4 bg-navy-sidebar text-[#F7F5F2] p-5 flex flex-col justify-between space-y-6">
                <div className="space-y-4">
                  {/* Avatar Placeholder */}
                  <div className="w-12 h-12 rounded-full bg-white/10 border border-white/20 flex items-center justify-center font-bold text-sm tracking-wider">
                    AL
                  </div>

                  <div>
                    <h3 className="font-bold text-sm text-white tracking-tight leading-tight">
                      Dr. Astrid Lindholm
                    </h3>
                    <p className="text-[10px] text-white/70 mt-0.5">
                      Staff Systems Architect
                    </p>
                  </div>

                  {/* Contact Meta */}
                  <div className="space-y-1.5 text-[9px] text-white/60 pt-2 border-t border-white/10">
                    <p>Zurich, Switzerland</p>
                    <p>astrid@systems.io</p>
                    <p>lindholm.ch</p>
                  </div>

                  {/* Skills Capsule Highlights */}
                  <div className="space-y-2 pt-2 border-t border-white/10">
                    <div className="text-[9px] uppercase tracking-wider font-bold text-white/80">
                      Core Competencies
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {['Distributed Systems', 'Rust / Tokio', 'Raft Consensus', 'Formal Verification'].map(
                        (skill) => (
                          <span
                            key={skill}
                            className="text-[8px] bg-white/10 border border-white/15 px-1.5 py-0.5 rounded-sm text-white/90"
                          >
                            {skill}
                          </span>
                        )
                      )}
                    </div>
                  </div>
                </div>

                {/* Education */}
                <div className="text-[9px] text-white/60 pt-2 border-t border-white/10">
                  <div className="font-bold text-white/80 text-[9px]">Ph.D. Computer Science</div>
                  <div>ETH Zurich, 2018</div>
                </div>
              </div>

              {/* Main Body Paper Surface (#FFFFFF) */}
              <div className="col-span-8 p-6 space-y-5 flex flex-col justify-between text-ink">
                {/* Executive Summary */}
                <div className="space-y-1.5">
                  <div className="w-full bg-[#EAE7E2] px-2.5 py-1 rounded-sm text-[10px] font-bold uppercase tracking-wider text-ink">
                    Executive Summary
                  </div>
                  <p className="text-[10px] text-ink-body leading-relaxed">
                    Systems architect with 12+ years pioneering consensus engines and low-latency storage.
                    Primary author of high-throughput serialization pipelines serving 40M req/sec.
                  </p>
                </div>

                {/* Work Experience with Light Gray Section Bar */}
                <div className="space-y-3">
                  <div className="w-full bg-[#EAE7E2] px-2.5 py-1 rounded-sm text-[10px] font-bold uppercase tracking-wider text-ink">
                    Selected Engineering Impact
                  </div>

                  <div className="space-y-1">
                    <div className="flex items-baseline justify-between text-[11px] font-bold text-ink">
                      <span>Staff Infrastructure Architect</span>
                      <span className="text-[9px] text-ink-muted font-normal">2021 — Present</span>
                    </div>
                    <div className="text-[10px] text-accent font-semibold">
                      Helix Cloud Infrastructure &bull; Zurich
                    </div>
                    <ul className="text-[9.5px] text-ink-body space-y-1 pt-1 list-disc list-inside">
                      <li>
                        Architected zero-downtime consensus engine spanning 28 worldwide regions with 99.999% SLA.
                      </li>
                      <li>
                        Eliminated p99 tail latency by 42% via custom zero-copy memory buffers.
                      </li>
                    </ul>
                  </div>

                  <div className="space-y-1 pt-1">
                    <div className="flex items-baseline justify-between text-[11px] font-bold text-ink">
                      <span>Senior Distributed Engineer</span>
                      <span className="text-[9px] text-ink-muted font-normal">2018 — 2021</span>
                    </div>
                    <div className="text-[10px] text-ink-muted">Aether Distributed Labs</div>
                    <ul className="text-[9.5px] text-ink-body space-y-1 pt-1 list-disc list-inside">
                      <li>
                        Designed distributed log compaction protocols deployed to 12,000 multi-tenant nodes.
                      </li>
                    </ul>
                  </div>
                </div>

                {/* Publications Bar */}
                <div className="space-y-1.5">
                  <div className="w-full bg-[#EAE7E2] px-2.5 py-1 rounded-sm text-[10px] font-bold uppercase tracking-wider text-ink">
                    Selected Publications
                  </div>
                  <p className="text-[9px] text-ink-body">
                    &ldquo;Deterministic Replay in Byzantine Fault Tolerant Systems&rdquo; &mdash; <em>USENIX ATC &rsquo;24</em>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Editorial Philosophy / Pillars Section (140px spacing) */}
      <section id="editorial-craft" className="py-30 md:py-35 border-t border-paper-border px-6 md:px-16 max-w-7xl mx-auto w-full space-y-16">
        <div className="max-w-2xl space-y-3">
          <div className="text-xs font-bold uppercase tracking-wider text-accent">
            Pillars of Editorial Craft
          </div>
          <h2 className="text-3xl md:text-5xl font-bold tracking-tighter text-ink leading-tight">
            Designed like a fine publication, not a spreadsheet.
          </h2>
          <p className="font-editorial-body text-base md:text-lg">
            Traditional resume builders mutate your text into broken containers. MirrorCV treats
            your document as structured data and formats it with typographic discipline.
          </p>
        </div>

        {/* 3 Editorial Cards (14px radius, hairline border, surface background) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="editorial-card p-8 space-y-4">
            <div className="w-10 h-10 rounded-pill bg-paper border border-paper-border flex items-center justify-center text-ink font-bold text-sm">
              01
            </div>
            <h3 className="font-bold text-xl text-ink tracking-tight">
              Sub-Point Typography
            </h3>
            <p className="text-sm text-ink-body leading-relaxed">
              Base font sizes calibrated from 8.0 to 12.0 pt with linked offset controls for candidate names,
              roles, dates, and bullets. Never guess if text fits.
            </p>
          </div>

          <div className="editorial-card p-8 space-y-4">
            <div className="w-10 h-10 rounded-pill bg-paper border border-paper-border flex items-center justify-center text-ink font-bold text-sm">
              02
            </div>
            <h3 className="font-bold text-xl text-ink tracking-tight">
              Deterministic Vector Parity
            </h3>
            <p className="text-sm text-ink-body leading-relaxed">
              The preview on your screen and the downloaded PDF are compiled through the exact same
              Playwright vector pipeline. Every word matches within 0.65 pt.
            </p>
          </div>

          <div className="editorial-card p-8 space-y-4">
            <div className="w-10 h-10 rounded-pill bg-paper border border-paper-border flex items-center justify-center text-ink font-bold text-sm">
              03
            </div>
            <h3 className="font-bold text-xl text-ink tracking-tight">
              Grounded AI Guardrails
            </h3>
            <p className="text-sm text-ink-body leading-relaxed">
              AI tools that sharpen impact verbs without inventing false metrics. Every rewrite presents
              an audited visual diff requiring your explicit approval.
            </p>
          </div>
        </div>
      </section>

      {/* 4. Live Vector Parity Section (140px spacing) */}
      <section id="vector-parity" className="py-30 md:py-35 border-t border-paper-border bg-paper-surface px-6 md:px-16">
        <div className="max-w-7xl mx-auto space-y-12">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div className="max-w-2xl space-y-3">
              <div className="text-xs font-bold uppercase tracking-wider text-accent">
                Zero Surprises
              </div>
              <h2 className="text-3xl md:text-5xl font-bold tracking-tighter text-ink leading-tight">
                What you compose is what recruiters read.
              </h2>
              <p className="font-editorial-body text-base">
                Web browsers render CSS dynamically; PDF viewers require absolute vector geometry.
                MirrorCV bridges both worlds seamlessly.
              </p>
            </div>

            <Link
              href="/dashboard"
              className="btn-secondary !text-xs !py-2.5 !px-5 self-start md:self-auto"
            >
              <span>Test Live in Editor</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* Parity Feature Comparison Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 pt-4">
            <div className="p-6 bg-paper rounded-card border border-paper-border space-y-2">
              <div className="text-2xl font-black tracking-tighter text-ink">&le; 0.65 pt</div>
              <div className="font-bold text-xs uppercase tracking-wider text-ink-muted">
                Coordinate Accuracy
              </div>
              <p className="text-xs text-ink-body">
                Max horizontal and vertical delta between DOM elements and PDF glyph streams.
              </p>
            </div>

            <div className="p-6 bg-paper rounded-card border border-paper-border space-y-2">
              <div className="text-2xl font-black tracking-tighter text-ink">100%</div>
              <div className="font-bold text-xs uppercase tracking-wider text-ink-muted">
                Embedded Fonts
              </div>
              <p className="text-xs text-ink-body">
                15 curated typography families bundled locally with zero external Google Fonts CDN calls.
              </p>
            </div>

            <div className="p-6 bg-paper rounded-card border border-paper-border space-y-2">
              <div className="text-2xl font-black tracking-tighter text-ink">1:1</div>
              <div className="font-bold text-xs uppercase tracking-wider text-ink-muted">
                Page Count Match
              </div>
              <p className="text-xs text-ink-body">
                Orphan-preventing print rules ensure no stray blank pages or chopped bullet points.
              </p>
            </div>

            <div className="p-6 bg-paper rounded-card border border-paper-border space-y-2">
              <div className="text-2xl font-black tracking-tighter text-ink">Zero</div>
              <div className="font-bold text-xs uppercase tracking-wider text-ink-muted">
                Third-Party CDNs
              </div>
              <p className="text-xs text-ink-body">
                Private, self-contained architecture with complete data privacy and offline readiness.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 5. Editorial Quote / Statement Section (140px spacing) */}
      <section className="py-30 md:py-35 border-t border-paper-border px-6 md:px-16 text-center max-w-4xl mx-auto">
        <blockquote className="space-y-6">
          <p className="font-editorial-headline text-2xl md:text-4xl text-ink leading-tight tracking-tight">
            &ldquo;A resume is not a billboard. It is a document of record &mdash; and its dignity
            arises from proportion, silence, and typographic integrity.&rdquo;
          </p>
          <footer className="text-xs font-semibold uppercase tracking-widest text-ink-muted">
            The MirrorCV Design Philosophy
          </footer>
        </blockquote>
      </section>

      {/* 6. Closing Call to Action (140px spacing) */}
      <section className="py-30 md:py-35 border-t border-paper-border bg-paper-surface px-6 md:px-16">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <h2 className="text-4xl md:text-6xl font-bold tracking-tighter text-ink leading-tight">
            Ready to craft your most refined resume?
          </h2>
          <p className="font-editorial-body text-base md:text-lg max-w-xl mx-auto">
            Experience the calm of an editorial workflow. Start completely free with local browser storage.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="btn-primary !text-base !py-3.5 !px-8 shadow-sm"
            >
              <span>Launch MirrorCV Workspace</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/templates"
              className="btn-secondary !text-base !py-3.5 !px-7"
            >
              <span>Browse Template Library</span>
            </Link>
          </div>
        </div>
      </section>

      {/* 7. Minimal Editorial Footer */}
      <footer className="border-t border-paper-border bg-paper px-6 md:px-16 py-12 flex flex-col md:flex-row items-center justify-between gap-6 text-xs text-ink-muted">
        <div className="flex items-center gap-2.5">
          <span className="font-bold text-sm tracking-tight text-ink">MirrorCV</span>
          <span>&bull;</span>
          <span>Phase F Editorial Edition</span>
        </div>

        <div className="flex flex-wrap items-center gap-6">
          <Link href="/dashboard" className="hover:text-ink transition-colors">
            Workspace
          </Link>
          <Link href="/templates" className="hover:text-ink transition-colors">
            Templates
          </Link>
          <Link href="/tailor" className="hover:text-ink transition-colors">
            DOCX Tailor
          </Link>
          <Link href="/credits" className="hover:text-ink transition-colors">
            Credits & ESCO
          </Link>
        </div>

        <div>
          &copy; {new Date().getFullYear()} MirrorCV. Built with editorial discipline.
        </div>
      </footer>
    </div>
  );
}

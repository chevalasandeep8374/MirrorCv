'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  CheckCircle2,
  ChevronDown,
  Sparkles,
  ShieldCheck,
  FileText,
  Sliders,
  Check,
  Zap,
  ArrowUpRight,
  ExternalLink,
  Code2,
  FileCheck2,
  Search,
  Lock,
  Minus,
  Plus,
  RefreshCw,
  Eye,
  SlidersHorizontal
} from 'lucide-react';

export default function LandingPage() {
  // Navigation & Dropdown states
  const [productMenuOpen, setProductMenuOpen] = useState(false);
  const [activeHeroTab, setActiveHeroTab] = useState<'content' | 'customize' | 'ai' | 'overview'>('content');

  // Feature 01: Before/After Slider state (0 to 100)
  const [sliderPos, setSliderPos] = useState(50);

  // Pricing Interval Toggle: 'monthly' | 'quarterly'
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'quarterly'>('quarterly');

  // FAQ Accordion state
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  return (
    <div className="min-h-screen bg-page text-slate-900 font-sans selection:bg-primary/10 selection:text-primary flex flex-col">
      {/* ====================================================================
          1. STICKY GLASS-1 HEADER
          ==================================================================== */}
      <header className="sticky top-0 z-50 glass-1 h-16 px-6 md:px-12 flex items-center justify-between border-b border-border-subtle">
        <div className="w-full max-w-7xl mx-auto flex items-center justify-between">
          {/* Left: Wordmark */}
          <div className="flex items-center gap-10">
            <Link href="/" className="flex items-center gap-2 group">
              <span className="font-heading font-extrabold text-2xl tracking-tight text-slate-950">
                MirrorCV
              </span>
              <span className="w-2 h-2 rounded-full bg-primary inline-block group-hover:scale-125 transition-transform" />
            </Link>

            {/* Desktop Navigation Links */}
            <nav className="hidden lg:flex items-center gap-8 text-sm font-semibold text-slate-600">
              {/* Product Dropdown */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setProductMenuOpen(!productMenuOpen)}
                  onBlur={() => setTimeout(() => setProductMenuOpen(false), 200)}
                  className="flex items-center gap-1 hover:text-slate-950 transition-colors focus-ring rounded-sm py-1 px-1.5"
                >
                  <span>Product</span>
                  <ChevronDown className={`w-3.5 h-3.5 transition-transform ${productMenuOpen ? 'rotate-180' : ''}`} />
                </button>

                {/* Glass-2 Dropdown Menu */}
                {productMenuOpen && (
                  <div className="absolute top-full left-0 mt-2 w-72 glass-2 rounded-card p-2 shadow-card z-50 animate-in fade-in zoom-in-95 duration-150">
                    <Link
                      href="/#tailor-to-job"
                      className="flex items-start gap-3 p-2.5 rounded-lg hover:bg-slate-50 transition-colors"
                    >
                      <div className="w-8 h-8 rounded-md bg-blue-50 text-primary flex items-center justify-center shrink-0 mt-0.5">
                        <Sparkles className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-950">Tailor to a Job</div>
                        <div className="text-[11px] text-slate-500 leading-snug mt-0.5">
                          Adversarially verified bullet point targeting with zero false claims.
                        </div>
                      </div>
                    </Link>

                    <Link
                      href="/#keep-template"
                      className="flex items-start gap-3 p-2.5 rounded-lg hover:bg-slate-50 transition-colors"
                    >
                      <div className="w-8 h-8 rounded-md bg-purple-50 text-accent-pill-text flex items-center justify-center shrink-0 mt-0.5">
                        <FileCheck2 className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-950">Keep Your Template</div>
                        <div className="text-[11px] text-slate-500 leading-snug mt-0.5">
                          Upload existing DOCX resumes with byte-level XML structure preservation.
                        </div>
                      </div>
                    </Link>

                    <Link
                      href="/dashboard"
                      className="flex items-start gap-3 p-2.5 rounded-lg hover:bg-slate-50 transition-colors"
                    >
                      <div className="w-8 h-8 rounded-md bg-emerald-50 text-emerald-700 flex items-center justify-center shrink-0 mt-0.5">
                        <SlidersHorizontal className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-950">FlowCV-Class Editor</div>
                        <div className="text-[11px] text-slate-500 leading-snug mt-0.5">
                          Dual-pane typography controls with sub-millimeter print parity.
                        </div>
                      </div>
                    </Link>
                  </div>
                )}
              </div>

              <a href="#how-it-works" className="hover:text-slate-950 transition-colors">
                Why MirrorCV
              </a>
              <a href="#pricing" className="hover:text-slate-950 transition-colors">
                Pricing
              </a>
              <Link href="/changelog" className="hover:text-slate-950 transition-colors">
                Changelog
              </Link>
            </nav>
          </div>

          {/* Right Header CTAs */}
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="text-xs font-semibold text-slate-800 hover:text-slate-950 px-3 py-2 rounded-btn transition-colors"
            >
              Log in
            </Link>
            <Link
              href="/signup"
              className="btn-primary !text-xs !py-2 !px-4"
            >
              <span>Get started free</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </header>

      {/* ====================================================================
          2. HERO SECTION WITH AMBIENT RADIAL BACKDROP
          ==================================================================== */}
      <section className="relative overflow-hidden pt-12 md:pt-20 pb-20 md:pb-28" style={{ background: 'var(--ambient-hero)' }}>
        <div className="max-w-7xl mx-auto px-6 md:px-12 text-center">
          {/* Announcement Pill */}
          <div className="flex justify-center mb-6">
            <Link
              href="/changelog#flowcv-editor-v2"
              className="inline-flex items-center gap-2.5 px-3.5 py-1 rounded-full glass-card hover:border-slate-300 transition-all text-xs font-semibold text-pill-purple shadow-sm"
            >
              <span className="bg-primary text-white text-[10px] font-extrabold px-2 py-0.5 rounded-full uppercase tracking-wider">
                NEW
              </span>
              <span>FlowCV-Class Editor Engine with Sub-Millimeter Parity &rarr;</span>
            </Link>
          </div>

          {/* Main Hero Headline (Option A - Direct & High-Converting) */}
          <h1 className="font-heading font-extrabold text-4xl sm:text-5xl md:text-6xl lg:text-[68px] tracking-tight leading-[1.08] text-slate-950 max-w-4xl mx-auto mb-6">
            Your resume. Exact template. Tailored in seconds.
          </h1>

          {/* Subcopy */}
          <p className="text-base sm:text-lg md:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed mb-8">
            Keep the typography and layout you spent hours perfecting. Tailor bullet points to any job
            description with verifiable facts—exported to native PDF and byte-preserved DOCX.
          </p>

          {/* Primary Action Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-4 mb-8">
            <Link
              href="/signup"
              className="btn-primary !text-base !py-3.5 !px-8 shadow-btn"
            >
              <span>Start tailoring free</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a
              href="#workspace-stage"
              className="btn-secondary !text-base !py-3.5 !px-7"
            >
              <span>See it in action</span>
            </a>
          </div>

          {/* True Micro-Claims Row */}
          <div className="flex flex-wrap items-center justify-center gap-6 md:gap-10 text-xs font-medium text-slate-600 mb-14">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
              <span>Sub-millimeter PDF parity (&le; 0.65 pt)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
              <span>Zero hallucinated metrics</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
              <span>15 self-hosted open fonts</span>
            </div>
          </div>

          {/* ====================================================================
              3. HERO STAGE (AUTHENTIC DUAL-PANE FLOWCV-CLASS RESUME EDITOR)
              ==================================================================== */}
          <div id="workspace-stage" className="w-full max-w-6xl mx-auto text-left">
            <div className="bg-stage rounded-stage border border-stage-border p-4 md:p-6 shadow-stage" style={{ background: 'var(--ambient-stage)' }}>
              {/* Stage Top Caption */}
              <div className="flex items-center justify-between pb-3 px-1">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-purple-900">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  <span>Live Workspace Preview</span>
                </div>
                <div className="text-xs font-bold text-purple-800">
                  01 / DUAL-PANE FLOWCV-CLASS EDITOR &rarr;
                </div>
              </div>

              {/* The Window Container */}
              <div className="bg-white rounded-xl border border-purple-200 shadow-xl overflow-hidden flex flex-col">
                {/* Window Top Bar (Glass-1) */}
                <div className="glass-1 h-12 px-4 flex items-center justify-between border-b border-border-subtle">
                  <div className="flex items-center gap-3">
                    {/* Window Controls */}
                    <div className="flex items-center gap-1.5 mr-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-red-400" />
                      <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                    </div>
                    <span className="font-bold text-xs text-slate-900">Principal Systems Engineer</span>
                    <span className="hidden sm:inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 text-[10px] font-semibold border border-emerald-200">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
                      All changes saved
                    </span>
                  </div>

                  {/* Tab Strip */}
                  <div className="flex items-center gap-1">
                    {(['content', 'customize', 'ai', 'overview'] as const).map((tab) => (
                      <button
                        key={tab}
                        type="button"
                        onClick={() => setActiveHeroTab(tab)}
                        className={`text-xs font-semibold px-3 py-1.5 rounded-md transition-colors capitalize ${
                          activeHeroTab === tab
                            ? 'text-primary bg-blue-50/80 font-bold'
                            : 'text-slate-600 hover:text-slate-900'
                        }`}
                      >
                        {tab === 'ai' ? 'AI Tools' : tab}
                      </button>
                    ))}
                  </div>

                  {/* Window Actions */}
                  <div className="flex items-center gap-2">
                    <span className="hidden md:inline-block text-[11px] text-slate-500 font-medium px-2 py-1 bg-slate-50 border border-slate-200 rounded">
                      Zoom 100%
                    </span>
                    <Link
                      href="/dashboard"
                      className="btn-primary !text-[11px] !py-1 !px-3"
                    >
                      Export PDF
                    </Link>
                  </div>
                </div>

                {/* Dual-Pane Editor Body */}
                <div className="grid grid-cols-1 lg:grid-cols-12 min-h-[520px] bg-slate-50/50">
                  {/* Left Column (5 cols): Editor Form Cards */}
                  <div className="lg:col-span-5 p-4 md:p-5 border-r border-border-subtle space-y-4 bg-slate-50/30 overflow-y-auto">
                    {/* Work Experience Card */}
                    <div className="frosted-card rounded-lg p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-xs text-slate-950 flex items-center gap-2">
                          💼 Work Experience
                        </span>
                        <span className="text-[10px] font-bold uppercase tracking-wider text-pill-purple bg-purple-50 px-2 py-0.5 rounded">
                          Targeted
                        </span>
                      </div>

                      <div className="border border-slate-200 rounded-md p-3 bg-white space-y-2">
                        <div className="flex items-baseline justify-between text-xs font-bold text-slate-900">
                          <span>Lead Systems Engineer</span>
                          <span className="text-[10px] text-slate-400 font-normal">2021 &ndash; Present</span>
                        </div>
                        <div className="text-[11px] text-primary font-semibold">
                          Apex Cloud Systems &bull; Full-time
                        </div>

                        {/* Verified Diff Highlight Box */}
                        <div className="mt-2 bg-emerald-50/60 border border-emerald-200 rounded p-2.5 text-[11px] text-slate-800 space-y-1">
                          <div className="flex items-center gap-1.5 text-[10px] font-extrabold text-emerald-800 uppercase tracking-wide">
                            <Check className="w-3 h-3 text-emerald-600 stroke-[3]" />
                            <span>94% Job Match &bull; Verifier Approved</span>
                          </div>
                          <p className="leading-relaxed">
                            Engineered multi-region Raft consensus replication engine{' '}
                            <span className="bg-emerald-200/60 font-semibold px-1 rounded text-emerald-950">
                              reducing p99 tail latency by 42%
                            </span>{' '}
                            across 12 distributed clusters.
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Technical Skills Card */}
                    <div className="frosted-card rounded-lg p-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-xs text-slate-950">
                          ⚡ Core Technical Skills
                        </span>
                        <span className="text-[10px] text-slate-400 font-semibold">5 matched</span>
                      </div>
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {['Rust', 'Go', 'Raft Protocol', 'Distributed Consensus', 'Kubernetes'].map((skill) => (
                          <span
                            key={skill}
                            className="inline-flex items-center gap-1 text-[11px] font-semibold bg-white border border-slate-200 px-2 py-1 rounded text-slate-800"
                          >
                            <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Right Column (7 cols): Real Floating A4 Resume Document */}
                  <div className="lg:col-span-7 p-6 md:p-8 flex flex-col items-center justify-center relative bg-slate-100/70 overflow-hidden">
                    {/* The A4 Resume Sheet */}
                    <div className="w-full max-w-md bg-white rounded border border-slate-300 p-6 md:p-8 shadow-floating-preview space-y-4">
                      {/* Resume Header */}
                      <div className="border-b-2 border-slate-900 pb-3">
                        <h2 className="font-heading font-extrabold text-xl text-slate-950 tracking-tight">
                          ALEX RIVERA
                        </h2>
                        <div className="text-[11px] font-bold text-primary uppercase tracking-wider mt-0.5">
                          Principal Systems Engineer
                        </div>
                        <div className="text-[9.5px] text-slate-500 flex flex-wrap gap-2 mt-1">
                          <span>alex.rivera@example.com</span> &bull;
                          <span>(555) 234-5678</span> &bull;
                          <span>Seattle, WA</span> &bull;
                          <span>linkedin.com/in/alexrivera</span>
                        </div>
                      </div>

                      {/* Work Experience on Resume */}
                      <div className="space-y-1.5">
                        <div className="text-[10px] font-extrabold uppercase tracking-wider text-slate-950 border-b border-slate-200 pb-1">
                          Professional Experience
                        </div>
                        <div className="flex items-baseline justify-between text-[10.5px]">
                          <span className="font-bold text-slate-900">Lead Systems Engineer &mdash; Apex Cloud Systems</span>
                          <span className="text-[9px] text-slate-500">2021 &ndash; Present</span>
                        </div>
                        <ul className="text-[9.5px] text-slate-700 space-y-1 list-disc list-inside leading-snug">
                          <li>
                            Engineered multi-region Raft consensus replication engine reducing p99 tail latency by 42% across 12 distributed clusters.
                          </li>
                          <li>
                            Architected asynchronous message serialization pipeline processing 3.4M writes/sec with zero data loss.
                          </li>
                        </ul>
                      </div>

                      {/* Core Competencies on Resume */}
                      <div className="space-y-1">
                        <div className="text-[10px] font-extrabold uppercase tracking-wider text-slate-950 border-b border-slate-200 pb-1">
                          Core Competencies
                        </div>
                        <p className="text-[9.5px] text-slate-700 leading-relaxed">
                          <strong>Systems & Infrastructure:</strong> Rust, Go, Raft Protocol, Distributed Consensus, Kubernetes, Linux eBPF, PostgreSQL.
                        </p>
                      </div>
                    </div>

                    {/* Floating Glass-1 Preview Toolbar */}
                    <div className="absolute bottom-4 glass-1 px-4 py-1.5 rounded-full shadow-card flex items-center gap-3 text-xs font-semibold text-slate-700">
                      <span className="hover:text-slate-950 cursor-pointer">&minus;</span>
                      <span>100%</span>
                      <span className="hover:text-slate-950 cursor-pointer">&#43;</span>
                      <span className="w-px h-3 bg-slate-300" />
                      <span className="hover:text-slate-950 cursor-pointer">Fit Width</span>
                      <span className="w-px h-3 bg-slate-300" />
                      <span className="text-[11px] text-slate-500">Page 1 / 1</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ====================================================================
          4. NUMBERED FEATURE TRIO (01, 02, 03) WITH CODED MINI-ILLUSTRATIONS
          ==================================================================== */}
      <section className="py-24 md:py-32 max-w-7xl mx-auto px-6 md:px-12 space-y-32">
        {/* --- Feature 01: Keep Your Template (Interactive Before/After Slider) --- */}
        <div id="keep-template" className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          <div className="lg:col-span-5 space-y-4">
            <div className="text-xs font-bold uppercase tracking-wider text-primary">
              01 / TEMPLATE FIDELITY
            </div>
            <h2 className="font-heading font-extrabold text-3xl md:text-4xl text-slate-950 tracking-tight leading-tight">
              Upload your existing DOCX. Keep every millimeter.
            </h2>
            <p className="text-slate-600 text-base leading-relaxed">
              Most resume tools force you to start over or strip your formatting into generic web templates.
              MirrorCV parses your original Word XML—preserving your exact fonts, margins, tab stops, and bullet indents down to the byte.
            </p>
            <div className="pt-2">
              <Link
                href="/tailor"
                className="inline-flex items-center gap-2 text-sm font-bold text-primary hover:text-primary-hover"
              >
                <span>Upload a DOCX to test template preservation</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          {/* Interactive Before/After Coded Illustration */}
          <div className="lg:col-span-7 bg-stage rounded-card p-6 border border-stage-border">
            <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm space-y-3">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-500 pb-2 border-b border-slate-100">
                <span>Original Word DOCX ({sliderPos}%)</span>
                <span>MirrorCV Preserved Output ({100 - sliderPos}%)</span>
              </div>

              {/* Visual Split Container */}
              <div className="relative h-64 bg-slate-50 rounded-lg overflow-hidden border border-slate-200 select-none">
                {/* Left Side: Raw DOCX Style */}
                <div
                  className="absolute inset-0 bg-white p-6 font-serif overflow-hidden"
                  style={{ clipPath: `polygon(0 0, ${sliderPos}% 0, ${sliderPos}% 100%, 0 100%)` }}
                >
                  <div className="text-xs text-blue-900 font-bold uppercase tracking-widest pb-1 border-b border-blue-900">
                    Microsoft Word &bull; Times New Roman 11pt
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 mt-2">ALEXANDER RIVERA</h3>
                  <p className="text-xs text-slate-600">Senior Infrastructure Engineer &bull; Seattle, WA</p>
                  <div className="text-xs font-bold text-blue-900 mt-3 border-b border-slate-300 pb-0.5">
                    TECHNICAL EXPERIENCE
                  </div>
                  <p className="text-[11px] text-slate-800 mt-1">
                    &bull; Maintained distributed consensus protocol for 12 core clusters.
                  </p>
                </div>

                {/* Right Side: Preserved Vector Parity Style */}
                <div
                  className="absolute inset-0 bg-slate-50/90 p-6 font-sans overflow-hidden"
                  style={{ clipPath: `polygon(${sliderPos}% 0, 100% 0, 100% 100%, ${sliderPos}% 100%)` }}
                >
                  <div className="text-xs text-primary font-bold uppercase tracking-widest pb-1 border-b border-primary">
                    MirrorCV Engine &bull; Byte-Exact Tokenized XML
                  </div>
                  <h3 className="text-lg font-heading font-extrabold text-slate-950 mt-2">ALEXANDER RIVERA</h3>
                  <p className="text-xs text-slate-600">Senior Infrastructure Engineer &bull; Seattle, WA</p>
                  <div className="text-xs font-bold text-primary mt-3 border-b border-slate-300 pb-0.5">
                    TECHNICAL EXPERIENCE
                  </div>
                  <p className="text-[11px] text-slate-800 mt-1">
                    &bull; Maintained distributed consensus protocol for 12 core clusters.
                  </p>
                </div>

                {/* Slider Handle */}
                <div
                  className="absolute top-0 bottom-0 w-1 bg-primary cursor-ew-resize flex items-center justify-center shadow-lg"
                  style={{ left: `${sliderPos}%` }}
                >
                  <div className="w-7 h-7 rounded-full bg-primary text-white text-xs font-bold flex items-center justify-center shadow-md">
                    &harr;
                  </div>
                </div>
              </div>

              {/* Slider Range Control */}
              <div className="pt-2 flex items-center gap-4">
                <span className="text-xs font-semibold text-slate-500">Drag to inspect fidelity:</span>
                <input
                  type="range"
                  min="5"
                  max="95"
                  value={sliderPos}
                  onChange={(e) => setSliderPos(Number(e.target.value))}
                  className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-primary"
                />
              </div>
            </div>
          </div>
        </div>

        {/* --- Feature 02: Tailor to a Job (Factual Verifier Diff) --- */}
        <div id="tailor-to-job" className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          {/* Coded Mini-Illustration Left */}
          <div className="lg:col-span-7 bg-stage rounded-card p-6 border border-stage-border order-2 lg:order-1">
            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-primary" />
                  <span className="text-xs font-bold text-slate-900">Adversarial Bullet Verifier</span>
                </div>
                <span className="text-[10px] font-bold text-emerald-800 bg-emerald-100 px-2.5 py-0.5 rounded-full">
                  Zero Hallucinations
                </span>
              </div>

              {/* Diff Inspection Item */}
              <div className="border border-slate-200 rounded-lg p-3.5 space-y-2 bg-slate-50/50">
                <div className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                  Target Qualification: &ldquo;High-Throughput Distributed Raft Experience&rdquo;
                </div>

                {/* Original Bullet */}
                <div className="text-xs text-slate-500 line-through bg-red-50/50 p-2 rounded border border-red-100">
                  Built some backend APIs and assisted with database caching and messaging.
                </div>

                {/* Verified Tailored Bullet */}
                <div className="text-xs text-slate-900 bg-emerald-50/50 p-2.5 rounded border border-emerald-200 font-medium">
                  Engineered distributed Raft consensus replication pipeline{' '}
                  <span className="bg-emerald-200 font-bold px-1 rounded text-emerald-950">
                    handling 3.4M writes/sec with 0% data loss
                  </span>.
                </div>

                <div className="flex items-center justify-between text-[11px] pt-1">
                  <span className="text-emerald-700 font-semibold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Verified against uploaded background profile
                  </span>
                  <span className="text-slate-400 font-bold">Diff #3 of 3</span>
                </div>
              </div>
            </div>
          </div>

          {/* Copy Right */}
          <div className="lg:col-span-5 space-y-4 order-1 lg:order-2">
            <div className="text-xs font-bold uppercase tracking-wider text-primary">
              02 / FACTUAL TAILORING
            </div>
            <h2 className="font-heading font-extrabold text-3xl md:text-4xl text-slate-950 tracking-tight leading-tight">
              Target qualifications without inventing experience.
            </h2>
            <p className="text-slate-600 text-base leading-relaxed">
              Standard AI resume generators invent fake revenue numbers, non-existent team sizes, and skills you never had.
              MirrorCV uses a strict adversarial verifier that rejects unconfirmed claims—ensuring every bullet point is 100% defendable in an interview.
            </p>
            <div className="pt-2">
              <Link
                href="/signup"
                className="inline-flex items-center gap-2 text-sm font-bold text-primary hover:text-primary-hover"
              >
                <span>Try job tailoring free</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>

        {/* --- Feature 03: ATS Checker (Clean Structural Readability) --- */}
        <div id="ats-checker" className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          <div className="lg:col-span-5 space-y-4">
            <div className="text-xs font-bold uppercase tracking-wider text-primary">
              03 / MACHINE READABILITY
            </div>
            <h2 className="font-heading font-extrabold text-3xl md:text-4xl text-slate-950 tracking-tight leading-tight">
              Standard structure that ATS parsers read cleanly.
            </h2>
            <p className="text-slate-600 text-base leading-relaxed">
              No hidden tables, corrupt icon glyphs, or multi-column layout traps that choke applicant tracking systems.
              Inspect your document’s exact plain-text extraction stream before submitting any application.
            </p>
            <div className="pt-2">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 text-sm font-bold text-primary hover:text-primary-hover"
              >
                <span>Test your resume ATS score</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          {/* Interactive ATS Checklist Illustration */}
          <div className="lg:col-span-7 bg-stage rounded-card p-6 border border-stage-border">
            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 font-extrabold text-xs flex items-center justify-center">
                    98%
                  </div>
                  <div>
                    <div className="text-xs font-bold text-slate-950">ATS Extraction Score</div>
                    <div className="text-[10px] text-slate-500">Taleo &bull; Workday &bull; Greenhouse Verified</div>
                  </div>
                </div>
                <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full">
                  100% Parseable
                </span>
              </div>

              {/* Checklist */}
              <div className="space-y-2 text-xs">
                {[
                  { label: 'Standard Section Headers', desc: 'Experience, Education, and Skills cleanly categorized' },
                  { label: 'Clean Date Formats', desc: 'Standardized ISO / Month-Year formats with no parsing drop-offs' },
                  { label: 'Zero Multi-Column Traps', desc: 'Linear reading order preserved in PyMuPDF text stream' },
                  { label: 'Standard Font Embedding', desc: 'All 15 font families self-hosted and fully embedded' },
                ].map((item) => (
                  <div key={item.label} className="flex items-start gap-2.5 p-2 rounded-lg bg-slate-50 border border-slate-100">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <div>
                      <div className="font-bold text-slate-900">{item.label}</div>
                      <div className="text-[11px] text-slate-500">{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ====================================================================
          5. HOW IT WORKS (HONEST 3-STEP WALKTHROUGH)
          ==================================================================== */}
      <section id="how-it-works" className="py-24 md:py-32 bg-slate-50/70 border-t border-border-subtle">
        <div className="max-w-7xl mx-auto px-6 md:px-12 space-y-16">
          <div className="text-center max-w-2xl mx-auto space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-primary">
              HOW IT WORKS
            </div>
            <h2 className="font-heading font-extrabold text-3xl md:text-5xl text-slate-950 tracking-tight">
              Three steps to a job-winning application.
            </h2>
            <p className="text-slate-600 text-base">
              No bloated wizards or locked templates. An honest, fast workflow built for career precision.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="bg-white rounded-card p-8 border border-slate-200 shadow-sm space-y-4 relative">
              <div className="w-10 h-10 rounded-lg bg-blue-50 text-primary font-heading font-extrabold text-lg flex items-center justify-center">
                1
              </div>
              <h3 className="font-heading font-extrabold text-xl text-slate-950 tracking-tight">
                Import or Choose Template
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Upload your existing Word resume (.docx) to keep your custom formatting, or pick from tested executive, single-column, or sidebar presets.
              </p>
            </div>

            {/* Step 2 */}
            <div className="bg-white rounded-card p-8 border border-slate-200 shadow-sm space-y-4 relative">
              <div className="w-10 h-10 rounded-lg bg-purple-50 text-accent-pill-text font-heading font-extrabold text-lg flex items-center justify-center">
                2
              </div>
              <h3 className="font-heading font-extrabold text-xl text-slate-950 tracking-tight">
                Target with Verified Facts
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Paste the target job description. MirrorCV scans qualification gaps and rewrites bullets with audited metrics—never inventing work history.
              </p>
            </div>

            {/* Step 3 */}
            <div className="bg-white rounded-card p-8 border border-slate-200 shadow-sm space-y-4 relative">
              <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-700 font-heading font-extrabold text-lg flex items-center justify-center">
                3
              </div>
              <h3 className="font-heading font-extrabold text-xl text-slate-950 tracking-tight">
                Export with 1:1 Parity
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Download a pixel-perfect native PDF or byte-preserved DOCX. What you see on screen is identical to the printed output within 0.65 pt.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ====================================================================
          6. PRICING SECTION (TRUE ENTITLEMENTS 3-TIER GRID)
          ==================================================================== */}
      <section id="pricing" className="py-24 md:py-32 max-w-7xl mx-auto px-6 md:px-12 space-y-16">
        <div className="text-center max-w-2xl mx-auto space-y-4">
          <div className="text-xs font-bold uppercase tracking-wider text-primary">
            PRICING
          </div>
          <h2 className="font-heading font-extrabold text-3xl md:text-5xl text-slate-950 tracking-tight">
            Fair, honest pricing with zero traps.
          </h2>
          <p className="text-slate-600 text-base">
            No sneaky trial rollovers or watermark extortion. Free forever for essential resumes.
          </p>

          {/* Billing Interval Switch */}
          <div className="inline-flex items-center p-1 rounded-full bg-slate-100 border border-slate-200 mt-4">
            <button
              type="button"
              onClick={() => setBillingCycle('monthly')}
              className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all ${
                billingCycle === 'monthly'
                  ? 'bg-white text-slate-950 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Monthly
            </button>
            <button
              type="button"
              onClick={() => setBillingCycle('quarterly')}
              className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all ${
                billingCycle === 'quarterly'
                  ? 'bg-primary text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              3-Month Pass (Save 30%)
            </button>
          </div>
        </div>

        {/* 3-Tier Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch">
          {/* Tier 1: Free Beta */}
          <div className="bg-white rounded-card p-8 border border-slate-200 shadow-sm flex flex-col justify-between space-y-6">
            <div className="space-y-4">
              <div className="text-xs font-bold uppercase tracking-wider text-slate-500">Free Beta</div>
              <div className="flex items-baseline gap-1">
                <span className="font-heading font-extrabold text-4xl text-slate-950">$0</span>
                <span className="text-xs text-slate-500 font-semibold">/ free forever</span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Everything you need to craft, customize, and export clean professional resumes.
              </p>

              <div className="pt-4 border-t border-slate-100 space-y-2.5 text-xs text-slate-700">
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Up to 2 active resumes</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Full FlowCV-class editor & controls</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Standard PDF & DOCX export</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span className="font-bold text-slate-900">Zero watermarks, ever</span>
                </div>
              </div>
            </div>

            <Link
              href="/signup"
              className="btn-secondary !w-full !py-3 !text-sm text-center font-bold"
            >
              Get started free
            </Link>
          </div>

          {/* Tier 2: Pro Job Hunt Pass (FEATURED) */}
          <div className="bg-white rounded-card p-8 border-2 border-primary shadow-xl flex flex-col justify-between space-y-6 relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-white text-[10px] font-extrabold uppercase px-3 py-0.5 rounded-full tracking-wider shadow">
              Most Popular
            </div>

            <div className="space-y-4">
              <div className="text-xs font-bold uppercase tracking-wider text-primary">Pro Job Hunt Pass</div>
              <div className="flex items-baseline gap-1">
                <span className="font-heading font-extrabold text-4xl text-slate-950">
                  {billingCycle === 'monthly' ? '$14' : '$29'}
                </span>
                <span className="text-xs text-slate-500 font-semibold">
                  {billingCycle === 'monthly' ? '/ month' : '/ 3-month hunt pass'}
                </span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Target job postings, tailor bullets with verified facts, and maintain multiple versions.
              </p>

              <div className="pt-4 border-t border-slate-100 space-y-2.5 text-xs text-slate-700">
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-primary shrink-0" />
                  <span className="font-bold text-slate-900">Unlimited active resumes & versions</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-primary shrink-0" />
                  <span>Full job description tailoring & gap scanner</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-primary shrink-0" />
                  <span>Adversarial verifier & bullet improver</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-primary shrink-0" />
                  <span>Multi-format export (PDF, DOCX, JSON, TXT)</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-primary shrink-0" />
                  <span>Priority headless rendering queue</span>
                </div>
              </div>
            </div>

            <Link
              href="/signup?plan=pro"
              className="btn-primary !w-full !py-3 !text-sm text-center font-bold shadow-btn"
            >
              Start 7-day Pro trial &rarr;
            </Link>
          </div>

          {/* Tier 3: Lifetime / Team */}
          <div className="bg-white rounded-card p-8 border border-slate-200 shadow-sm flex flex-col justify-between space-y-6">
            <div className="space-y-4">
              <div className="text-xs font-bold uppercase tracking-wider text-slate-500">Lifetime Pass</div>
              <div className="flex items-baseline gap-1">
                <span className="font-heading font-extrabold text-4xl text-slate-950">$79</span>
                <span className="text-xs text-slate-500 font-semibold">/ one-time</span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Pay once, use forever. Ideal for career changers, consultants, and executives.
              </p>

              <div className="pt-4 border-t border-slate-100 space-y-2.5 text-xs text-slate-700">
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>All Pro features forever</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Master Career Profile repository</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Early access to all upcoming engines</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Commercial use license</span>
                </div>
              </div>
            </div>

            <Link
              href="/signup?plan=lifetime"
              className="btn-secondary !w-full !py-3 !text-sm text-center font-bold"
            >
              Get lifetime access
            </Link>
          </div>
        </div>
      </section>

      {/* ====================================================================
          7. FAQ ACCORDION
          ==================================================================== */}
      <section className="py-24 md:py-32 bg-slate-50/70 border-t border-border-subtle">
        <div className="max-w-4xl mx-auto px-6 md:px-12 space-y-12">
          <div className="text-center space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-primary">
              FREQUENTLY ASKED QUESTIONS
            </div>
            <h2 className="font-heading font-extrabold text-3xl md:text-4xl text-slate-950 tracking-tight">
              Honest answers to common questions.
            </h2>
          </div>

          <div className="space-y-4">
            {[
              {
                q: 'Will MirrorCV change my existing Word document layout?',
                a: 'No. When you upload an existing DOCX, MirrorCV parses the underlying OpenXML format and performs tokenized replacements without modifying your font choices, margin geometries, tab stops, or custom bullet styles.'
              },
              {
                q: 'Does the AI invent metrics or past work experience?',
                a: 'Never. Our pipeline enforces strict adversarial verification. If a generated bullet contains numbers or skills that cannot be verified against your profile history, the system flags it and asks you for the real number before accepting the change.'
              },
              {
                q: 'Are exported PDFs watermarked on the free plan?',
                a: 'No. Free and paid exports are 100% clean, professional, and completely unwatermarked. We do not hold your application hostage.'
              },
              {
                q: 'How does MirrorCV achieve sub-millimeter print parity?',
                a: 'We use the exact same headless Chromium vector engine for both the in-browser canvas and exported PDF files, with self-hosted font metrics and strict CSS page-break constraints.'
              },
              {
                q: 'Is my resume data kept private?',
                a: 'Yes. Resumes are stored locally in your browser and encrypted in our database if you create an account. We do not sell candidate data or train public AI models on your career history.'
              }
            ].map((faq, idx) => (
              <div
                key={faq.q}
                className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm"
              >
                <button
                  type="button"
                  onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                  className="w-full p-5 text-left font-bold text-sm text-slate-900 flex items-center justify-between gap-4 hover:bg-slate-50 transition-colors"
                >
                  <span>{faq.q}</span>
                  <span className="text-slate-400 font-normal text-lg">
                    {openFaq === idx ? '&minus;' : '&#43;'}
                  </span>
                </button>
                {openFaq === idx && (
                  <div className="px-5 pb-5 text-xs text-slate-600 leading-relaxed border-t border-slate-100 pt-3">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ====================================================================
          8. BOTTOM DARK BAND CALL-TO-ACTION
          ==================================================================== */}
      <section className="bg-dark-footer text-white py-24 md:py-32 px-6 md:px-12 relative overflow-hidden">
        <div className="max-w-4xl mx-auto text-center space-y-8 relative z-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full glass-dark text-xs font-semibold text-slate-200 border border-white/10">
            <Sparkles className="w-3.5 h-3.5 text-blue-400" />
            <span>Built for career precision &bull; No credit card required</span>
          </div>

          <h2 className="font-heading font-extrabold text-4xl sm:text-5xl md:text-6xl tracking-tight leading-tight">
            Ready for a resume that actually looks like your resume?
          </h2>

          <p className="text-slate-400 text-base md:text-lg max-w-xl mx-auto leading-relaxed">
            Experience the calm of a FlowCV-class editor with true vector parity and factual tailoring.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <Link
              href="/signup"
              className="btn-primary !text-base !py-3.5 !px-8 shadow-btn"
            >
              <span>Create your resume now</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-btn bg-white/10 hover:bg-white/15 text-white font-semibold text-base transition-colors border border-white/15"
            >
              <span>Open live workspace</span>
            </Link>
          </div>
        </div>
      </section>

      {/* ====================================================================
          9. FOOTER
          ==================================================================== */}
      <footer className="bg-white border-t border-slate-200 py-16 px-6 md:px-12 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-5 gap-8 mb-12">
          {/* Col 1: Wordmark & Mission */}
          <div className="col-span-2 space-y-3">
            <Link href="/" className="flex items-center gap-2">
              <span className="font-heading font-extrabold text-xl tracking-tight text-slate-950">
                MirrorCV
              </span>
              <span className="w-2 h-2 rounded-full bg-primary inline-block" />
            </Link>
            <p className="text-xs text-slate-500 max-w-sm leading-relaxed">
              FlowCV-class dual-pane editor with byte-exact template preservation and adversarial fact verification.
            </p>
          </div>

          {/* Col 2: Product */}
          <div className="space-y-3">
            <div className="font-bold uppercase tracking-wider text-slate-900 text-[11px]">Product</div>
            <ul className="space-y-2">
              <li><a href="#tailor-to-job" className="hover:text-slate-950">Tailor to a job</a></li>
              <li><a href="#keep-template" className="hover:text-slate-950">Keep your template</a></li>
              <li><Link href="/dashboard" className="hover:text-slate-950">FlowCV-class editor</Link></li>
              <li><a href="#ats-checker" className="hover:text-slate-950">ATS checker</a></li>
            </ul>
          </div>

          {/* Col 3: Resources */}
          <div className="space-y-3">
            <div className="font-bold uppercase tracking-wider text-slate-900 text-[11px]">Resources</div>
            <ul className="space-y-2">
              <li><Link href="/changelog" className="hover:text-slate-950">Changelog</Link></li>
              <li><a href="#pricing" className="hover:text-slate-950">Pricing</a></li>
              <li><a href="#how-it-works" className="hover:text-slate-950">Why MirrorCV</a></li>
              <li><Link href="/templates" className="hover:text-slate-950">Template Library</Link></li>
            </ul>
          </div>

          {/* Col 4: Legal & Privacy */}
          <div className="space-y-3">
            <div className="font-bold uppercase tracking-wider text-slate-900 text-[11px]">Privacy & Trust</div>
            <ul className="space-y-2">
              <li><span className="text-slate-400">Zero public model training</span></li>
              <li><span className="text-slate-400">Private encrypted storage</span></li>
              <li><span className="text-slate-400">Terms & Conditions</span></li>
              <li><span className="text-slate-400">Privacy Policy</span></li>
            </ul>
          </div>
        </div>

        <div className="max-w-7xl mx-auto pt-8 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>&copy; {new Date().getFullYear()} MirrorCV. Built for career precision.</div>
          <div className="flex items-center gap-4 text-[11px]">
            <Link href="/changelog#flowcv-editor-v2" className="hover:text-slate-950">
              v2.4 FlowCV Engine
            </Link>
            <span>&bull;</span>
            <span>Sub-millimeter Parity Standard</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

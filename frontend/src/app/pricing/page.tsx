'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Check, Sparkles, ArrowRight } from 'lucide-react';

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'quarterly'>('quarterly');

  return (
    <div className="min-h-screen bg-page text-slate-900 font-sans selection:bg-primary/10 selection:text-primary flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 glass-1 h-16 px-6 md:px-12 flex items-center justify-between border-b border-border-subtle">
        <div className="w-full max-w-6xl mx-auto flex items-center justify-between">
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

      {/* Main Container */}
      <main className="max-w-6xl mx-auto px-6 py-16 md:py-24 w-full space-y-16">
        <div className="text-center max-w-2xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-50 text-pill-purple border border-purple-200 text-xs font-bold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Simple, Fair Pricing</span>
          </div>
          <h1 className="font-heading font-extrabold text-4xl sm:text-5xl text-slate-950 tracking-tight">
            Plans built for serious job seekers.
          </h1>
          <p className="text-base text-slate-600">
            Free forever for basic resumes. Upgrade for verified tailoring, gap analysis, and unlimited export versions.
          </p>

          {/* Billing Switch */}
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
          {/* Free Beta */}
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

          {/* Pro Job Hunt Pass (Featured) */}
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

          {/* Lifetime Pass */}
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
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-12 px-6 text-center text-xs text-slate-500">
        <div>&copy; {new Date().getFullYear()} MirrorCV. Built for career precision.</div>
      </footer>
    </div>
  );
}

import React from 'react';
import Link from 'next/link';
import { MirrorCvLogo } from '@/components/brand/MirrorCvLogo';
import { ArrowLeft, ExternalLink, ShieldCheck, FileText, Database, Code, BookOpen, Type } from 'lucide-react';

export default function CreditsPage() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white sticky top-0 z-20 shadow-2xs">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Link
              href="/"
              className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 transition"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Dashboard</span>
            </Link>
          </div>
          <div className="flex items-center space-x-2">
            <MirrorCvLogo size="sm" asLink href="/dashboard" />
            <span className="text-sm font-semibold text-slate-500 pl-2 border-l border-slate-200">Legal & Credits</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-12 flex-1 w-full space-y-8">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Open Data, Schemas & Open Source Credits</h1>
          <p className="text-sm text-slate-600 mt-2">
            MirrorCV relies on curated open standards, standardized taxonomy datasets, and open-source infrastructure
            to deliver deterministic resume fidelity and tailoring.
          </p>
        </div>

        {/* ESCO European Commission Notice */}
        <div className="bg-white border border-blue-200 rounded-2xl p-6 shadow-2xs relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1.5 bg-blue-600" />
          <div className="flex items-start space-x-4">
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0 mt-0.5">
              <BookOpen className="w-5 h-5" />
            </div>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-bold text-slate-900">European Commission ESCO Classification Dataset</h2>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                  CC-BY 4.0
                </span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                MirrorCV incorporates technical skill definitions, concepts, and taxonomy classifications derived from the{' '}
                <strong>European Skills, Competences, Qualifications and Occupations (ESCO)</strong> classification dataset,
                provided by the European Commission.
              </p>
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs font-mono text-slate-700 space-y-1">
                <div><strong>Licensor:</strong> European Union, 2013-2026</div>
                <div><strong>License:</strong> Creative Commons Attribution 4.0 International (CC-BY 4.0)</div>
                <div>
                  <strong>Official Portal:</strong>{' '}
                  <a
                    href="https://ec.europa.eu/esco/portal"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline inline-flex items-center gap-1"
                  >
                    https://ec.europa.eu/esco/portal
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
              <p className="text-[11px] text-slate-500">
                In compliance with CC-BY 4.0 section 3(a), MirrorCV indicates that technical concepts and taxonomies have been
                curated and normalized into technical categories for explainable match scoring and gap analysis.
              </p>
            </div>
          </div>
        </div>

        {/* ECMA-376 Standard Notice */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-2xs">
          <div className="flex items-start space-x-4">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0 mt-0.5">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-bold text-slate-900">ECMA-376 & ISO/IEC 29500 Transitional Schemas</h2>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                  Standard XSD
                </span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                MirrorCV validates every generated DOCX document against the formal ECMA-376 / ISO/IEC 29500 Office Open XML
                Transitional XML Schemas (XSD) to guarantee full specification compliance, structural validity, and defect-free
                rendering in Microsoft Word and Google Docs.
              </p>
            </div>
          </div>
        </div>

        {/* LibreOffice & Rendering Engines */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-2xs">
          <div className="flex items-start space-x-4">
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0 mt-0.5">
              <Code className="w-5 h-5" />
            </div>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-bold text-slate-900">LibreOffice Headless Rendering Engine</h2>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
                  LGPLv3
                </span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                High-fidelity server-side PDF conversion and visual layout calibration are executed using headless
                LibreOffice (The Document Foundation), licensed under the GNU Lesser General Public License v3.0.
              </p>
            </div>
          </div>
        </div>

        {/* Database & Cloud Security */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-2xs">
          <div className="flex items-start space-x-4">
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0 mt-0.5">
              <Database className="w-5 h-5" />
            </div>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-bold text-slate-900">PostgreSQL & Supabase</h2>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200">
                  Apache 2.0 / PostgreSQL
                </span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Relational persistence, vector embeddings, storage policies, and row-level security (RLS) isolation are powered
                by PostgreSQL and Supabase.
              </p>
            </div>
          </div>
        </div>

        {/* Self-Hosted Fonts & SIL Open Font License (OFL) Notice */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-2xs">
          <div className="flex items-start space-x-4">
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0 mt-0.5">
              <Type className="w-5 h-5" />
            </div>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-bold text-slate-900">Self-Hosted Typography & SIL Open Font License (OFL)</h2>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
                  SIL OFL 1.1 / Apache 2.0
                </span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                MirrorCV bundles and self-hosts 16 curated open-source typeface families via <code>@fontsource</code> for zero-CDN,
                high-privacy document rendering and deterministic print exports across web and headless PDF pipelines:
              </p>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono text-slate-700 bg-slate-50 p-4 rounded-xl border border-slate-200">
                <div>• Inter (OFL 1.1)</div>
                <div>• Roboto (Apache 2.0)</div>
                <div>• Open Sans (OFL 1.1)</div>
                <div>• Lato (OFL 1.1)</div>
                <div>• Montserrat (OFL 1.1)</div>
                <div>• Source Sans 3 (OFL 1.1)</div>
                <div>• Poppins (OFL 1.1)</div>
                <div>• Merriweather (OFL 1.1)</div>
                <div>• Playfair Display (OFL)</div>
                <div>• Lora (OFL 1.1)</div>
                <div>• PT Serif (OFL 1.1)</div>
                <div>• Fira Sans (OFL 1.1)</div>
                <div>• Nunito (OFL 1.1)</div>
                <div>• Raleway (OFL 1.1)</div>
                <div>• Cinzel (OFL 1.1)</div>
                <div>• Noto Sans Devanagari (OFL)</div>
              </div>
              <p className="text-[11px] text-slate-500">
                All font families are self-hosted within the application package; no runtime third-party font CDN requests are made.
                Licensed under the SIL Open Font License 1.1 and Apache 2.0.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6">
        <div className="max-w-5xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-3">
          <div>© 2026 MirrorCV. Master-Template Resume Tailoring with Zero Layout Drift.</div>
          <div className="flex items-center space-x-4">
            <Link href="/" className="hover:text-slate-900 transition">Dashboard</Link>
            <Link href="/tailor" className="hover:text-slate-900 transition">Tailor</Link>
            <Link href="/credits" className="font-semibold text-blue-600 hover:text-blue-700 transition">Credits & Attribution</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

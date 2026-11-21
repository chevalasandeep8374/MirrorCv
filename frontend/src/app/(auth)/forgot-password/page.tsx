'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { MirrorCvLogo } from '@/components/brand/MirrorCvLogo';
import { Loader2, ArrowRight, CheckCircle2, AlertCircle, ArrowLeft } from 'lucide-react';
import { supabase } from '@/lib/supabase';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const { error: resetError } = await supabase.auth.resetPasswordForEmail(email.trim(), {
        redirectTo: `${typeof window !== 'undefined' ? window.location.origin : ''}/auth/callback?next=/account/reset-password`,
      });

      if (resetError) {
        setError(resetError.message);
        return;
      }

      setSubmitted(true);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to send reset instructions. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center p-4"
      style={{ background: 'var(--ambient-hero)' }}
    >
      <div className="w-full max-w-md bg-white border border-border-subtle rounded-card p-8 shadow-card">
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center mb-8">
          <MirrorCvLogo size="lg" asLink href="/" className="mb-4" />
          <h1 className="font-heading font-extrabold text-xl text-slate-900 tracking-tight">
            Reset Password
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Enter your email to receive recovery instructions
          </p>
        </div>

        {submitted ? (
          <div className="p-5 bg-emerald-50 border border-emerald-200 rounded-btn text-xs text-emerald-800 space-y-3">
            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-bold text-sm text-emerald-900">Recovery link sent</p>
                <p className="mt-1 leading-relaxed">
                  If an account exists for <span className="font-semibold">{email}</span>, you will
                  receive an email with instructions to reset your password.
                </p>
              </div>
            </div>
            <div className="pt-2">
              <Link
                href="/login"
                className="btn-primary w-full !py-2.5 flex items-center justify-center gap-1.5 !text-xs"
              >
                <span>Back to Sign In</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        ) : (
          <>
            {error && (
              <div className="mb-5 p-3.5 bg-rose-50 border border-rose-200 rounded-btn text-xs text-rose-700 font-medium leading-relaxed flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1.5" htmlFor="reset-email">
                  Email Address
                </label>
                <input
                  id="reset-email"
                  type="email"
                  required
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full border border-border-subtle rounded-btn px-3 py-2.5 text-slate-900 focus:outline-none focus:border-primary transition-colors text-xs"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full !py-3 flex items-center justify-center gap-2 mt-6 shadow-btn"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Sending instructions...</span>
                  </>
                ) : (
                  <>
                    <span>Send Reset Instructions</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            <div className="mt-8 pt-6 border-t border-border-subtle text-center text-xs text-slate-500">
              <Link
                href="/login"
                className="text-slate-600 hover:text-slate-900 font-medium inline-flex items-center gap-1.5"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Back to Sign In</span>
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

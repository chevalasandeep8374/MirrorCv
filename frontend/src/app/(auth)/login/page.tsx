'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { MirrorCvLogo } from '@/components/brand/MirrorCvLogo';
import { Loader2, ArrowRight, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { supabase } from '@/lib/supabase';

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextUrl = searchParams.get('next') || '/dashboard';
  const urlMessage = searchParams.get('message');

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if user is already authenticated
    supabase.auth.getSession().then(({ data }) => {
      if (data?.session?.user) {
        router.push(nextUrl);
      }
    });
  }, [router, nextUrl]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const { data, error: authError } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password,
      });

      if (authError) {
        if (authError.message.toLowerCase().includes('invalid login credentials')) {
          setError('Invalid email or password. Please check your credentials and try again.');
        } else if (authError.message.toLowerCase().includes('email not confirmed')) {
          setError('Email not confirmed. Please check your inbox for the confirmation link.');
        } else if (authError.message.toLowerCase().includes('rate limit')) {
          setError('Too many login attempts. Please wait a moment before trying again.');
        } else {
          setError(authError.message);
        }
        return;
      }

      if (data?.session) {
        router.push(nextUrl);
        router.refresh();
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred during login. Please try again.');
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
            Sign In to Your Workspace
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Access and customize your career resumes
          </p>
        </div>

        {urlMessage && !error && (
          <div className="mb-5 p-3.5 bg-amber-50 border border-amber-200 rounded-btn text-xs text-amber-800 font-medium leading-relaxed flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
            <span>{urlMessage}</span>
          </div>
        )}

        {error && (
          <div className="mb-5 p-3.5 bg-rose-50 border border-rose-200 rounded-btn text-xs text-rose-700 font-medium leading-relaxed flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-bold text-slate-700 mb-1.5" htmlFor="login-email">
              Email Address
            </label>
            <input
              id="login-email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full border border-border-subtle rounded-btn px-3 py-2.5 text-slate-900 focus:outline-none focus:border-primary transition-colors text-xs"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block font-bold text-slate-700" htmlFor="login-password">
                Password
              </label>
              <Link
                href="/forgot-password"
                className="text-[11px] text-primary hover:underline font-semibold"
              >
                Forgot password?
              </Link>
            </div>
            <div className="relative">
              <input
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full border border-border-subtle rounded-btn px-3 py-2.5 pr-10 text-slate-900 focus:outline-none focus:border-primary transition-colors text-xs"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 focus:outline-none"
                tabIndex={-1}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full !py-3 flex items-center justify-center gap-2 mt-6 shadow-btn"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Signing in...</span>
              </>
            ) : (
              <>
                <span>Sign In</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-border-subtle text-center text-xs text-slate-500">
          Don&apos;t have an account?{' '}
          <Link href="/register" className="text-primary font-bold hover:underline">
            Create an account
          </Link>
        </div>
      </div>
    </div>
  );
}

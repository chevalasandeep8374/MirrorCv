'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { MirrorCvLogo } from '@/components/brand/MirrorCvLogo';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { FileText, Loader2, ArrowRight } from 'lucide-react';
import { supabase } from '@/lib/supabase';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('alex@example.com');
  const [password, setPassword] = useState('password123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // 1. Primary: Authenticate with Supabase Auth
      const { data, error: supaError } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (!supaError && data?.session?.access_token) {
        localStorage.setItem('mirrorcv_token', data.session.access_token);
        localStorage.setItem('mirrorcv_user', JSON.stringify(data.user));
        router.push('/dashboard');
        return;
      }

      // 2. Secondary fallback: Legacy SQLite backend login (maintained during migration)
      try {
        const res = await axios.post(`${API_BASE_URL}/api/auth/login`, {
          email,
          password,
        });

        if (res.data?.access_token) {
          localStorage.setItem('mirrorcv_token', res.data.access_token);
          localStorage.setItem('mirrorcv_user', JSON.stringify(res.data.user));
          router.push('/dashboard');
          return;
        }
      } catch {
        if (supaError) {
          throw supaError;
        }
      }

      throw new Error('Authentication failed. Please verify email and password.');
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Login failed. Please try again.');
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

        {error && (
          <div className="mb-5 p-3.5 bg-rose-50 border border-rose-200 rounded-btn text-xs text-rose-700 font-medium leading-relaxed">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-bold text-slate-700 mb-1.5">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="alex@example.com"
              className="w-full px-3.5 py-2.5 bg-white border border-border-subtle rounded-btn focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary text-sm text-slate-900 transition-all"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block font-bold text-slate-700">
                Password
              </label>
              <a href="#" className="text-[11px] text-primary font-semibold hover:underline">
                Forgot password?
              </a>
            </div>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3.5 py-2.5 bg-white border border-border-subtle rounded-btn focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary text-sm text-slate-900 transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-primary hover:bg-primary-hover text-white font-bold text-sm rounded-btn shadow-btn transition-all disabled:opacity-50 flex items-center justify-center gap-2 mt-2"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <span>Sign In</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        <div className="mt-8 pt-5 border-t border-slate-100 text-center text-xs text-slate-500">
          <span>Don&apos;t have an account? </span>
          <Link href="/register" className="text-primary font-bold hover:underline">
            Register now
          </Link>
        </div>
      </div>
    </div>
  );
}

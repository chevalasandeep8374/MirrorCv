'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { MirrorCvLogo } from '@/components/brand/MirrorCvLogo';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { FileText, Loader2, ArrowRight, CheckCircle2 } from 'lucide-react';
import { supabase } from '@/lib/supabase';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      // 1. Primary: Register with Supabase Auth
      const { data, error: supaError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
          },
        },
      });

      if (!supaError) {
        if (data?.session?.access_token) {
          localStorage.setItem('mirrorcv_token', data.session.access_token);
          localStorage.setItem('mirrorcv_user', JSON.stringify(data.user));
          router.push('/dashboard');
          return;
        } else if (data?.user) {
          setSuccessMsg('Account created successfully! Please check your email or proceed to sign in.');
          return;
        }
      }

      // 2. Secondary fallback: Legacy SQLite registration
      try {
        const res = await axios.post(`${API_BASE_URL}/api/auth/register`, {
          email,
          password,
          full_name: fullName,
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

      throw new Error('Registration failed. Please try again.');
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Registration failed. Please try again.');
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
            Create Your Account
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Start tailoring resumes with verified facts and sub-millimeter parity
          </p>
        </div>

        {error && (
          <div className="mb-5 p-3.5 bg-rose-50 border border-rose-200 rounded-btn text-xs text-rose-700 font-medium leading-relaxed">
            {error}
          </div>
        )}

        {successMsg && (
          <div className="mb-5 p-3.5 bg-emerald-50 border border-emerald-200 rounded-btn text-xs text-emerald-800 font-medium leading-relaxed flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-bold text-slate-700 mb-1.5">
              Full Name
            </label>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Alex Rivera"
              className="w-full px-3.5 py-2.5 bg-white border border-border-subtle rounded-btn focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary text-sm text-slate-900 transition-all"
            />
          </div>

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
            <label className="block font-bold text-slate-700 mb-1.5">
              Password
            </label>
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
                <span>Get Started Free</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        <div className="mt-8 pt-5 border-t border-slate-100 text-center text-xs text-slate-500">
          <span>Already have an account? </span>
          <Link href="/login" className="text-primary font-bold hover:underline">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}

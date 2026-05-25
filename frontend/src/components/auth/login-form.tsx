"use client";

import type { FormEvent } from "react";
import { useState } from "react";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { AlertCircle, Eye, EyeOff, Loader2, School } from "lucide-react";

import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/authStore";

function safeInternalPath(raw: string | null, fallback: string) {
  if (!raw || !raw.startsWith("/") || raw.startsWith("//")) return fallback;
  return raw;
}

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const callbackUrl =
    safeInternalPath(searchParams.get("callbackUrl"), "") ||
    safeInternalPath(searchParams.get("next"), "/dashboard");

  const { login } = useAuthStore();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const appLabel = process.env.NEXT_PUBLIC_APP_NAME ?? "SRTAPP";

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      const result = await login(email, password);
      if (result.requires2fa) {
        router.push("/verify-2fa");
        return;
      }
      router.push(result.redirectTo ?? callbackUrl);
      router.refresh();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Invalid credentials. Please try again.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center">
            <img src="/logo.png" alt="SRT College" className="w-24 h-24 object-contain mix-blend-multiply" onError={(e) => { e.currentTarget.style.display="none"; }} />
          </div>
          <h2 className="mt-6 font-display text-3xl font-bold tracking-tight text-primary">
            SRT College, Dhmari
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">College management system</p>
        </div>

        <div className="rounded-2xl border border-border bg-surface p-8 shadow-card">
          {error ? (
            <div className="mb-6 flex items-center gap-2 rounded-lg bg-error/10 p-3 text-sm text-error">
              <AlertCircle className="h-4 w-4 shrink-0" aria-hidden />
              {error}
            </div>
          ) : null}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-foreground">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(ev) => setEmail(ev.target.value)}
                className="mt-2 block w-full rounded-lg border border-input bg-background px-4 py-3 text-sm outline-none transition-colors focus:border-accent focus:ring-1 focus:ring-accent"
                placeholder="you@college.edu"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-foreground">
                Password
              </label>
              <div className="relative mt-2">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(ev) => setPassword(ev.target.value)}
                  className="block w-full rounded-lg border border-input bg-background px-4 py-3 pr-12 text-sm outline-none transition-colors focus:border-accent focus:ring-1 focus:ring-accent"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  tabIndex={-1}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember"
                  name="remember"
                  type="checkbox"
                  className="h-4 w-4 rounded border-border text-accent focus:ring-accent"
                />
                <label htmlFor="remember" className="ml-2 text-sm text-muted-foreground">
                  Remember me
                </label>
              </div>
              <Link href="/forgot-password" className="text-sm font-medium text-accent hover:underline">
                Forgot password?
              </Link>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className={cn(
                "flex w-full items-center justify-center rounded-lg bg-accent px-4 py-3 text-sm font-semibold text-white shadow-sm transition-all hover:bg-accent/90 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-background",
                isLoading && "cursor-not-allowed opacity-70",
              )}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden />
                  Signing in…
                </>
              ) : (
                "Sign in"
              )}
            </button>
          </form>
        </div>

        <p className="text-center text-xs text-muted-foreground">
          Protected access. Unauthorized use is prohibited.</p>
        <p className="text-center text-sm text-muted-foreground">
          New student?{" "}
          <Link href="/register" className="font-medium text-accent hover:underline">
            Create account
          </Link>
        </p>
      </div>
    </div>
  );
}

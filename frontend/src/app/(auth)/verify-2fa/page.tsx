"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { AlertCircle, Loader2 } from "lucide-react";

import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/authStore";

const OTP_SECONDS = 300;

export default function Verify2FAPage() {
  const router = useRouter();
  const { verify2fa, pendingSessionKey } = useAuthStore();
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [secondsLeft, setSecondsLeft] = useState(OTP_SECONDS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!pendingSessionKey) {
      router.replace("/login");
    }
  }, [pendingSessionKey, router]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setSecondsLeft((value) => (value > 0 ? value - 1 : 0));
    }, 1000);
    return () => window.clearInterval(timer);
  }, []);

  const minutes = Math.floor(secondsLeft / 60);
  const seconds = String(secondsLeft % 60).padStart(2, "0");

  function updateDigit(index: number, value: string) {
    if (!/^\d?$/.test(value)) return;
    const next = [...otp];
    next[index] = value;
    setOtp(next);
  }

  async function handleVerify() {
    setError("");
    setLoading(true);
    try {
      const redirectTo = await verify2fa(otp.join(""));
      router.push(redirectTo);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Verification failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12">
      <div className="w-full max-w-md rounded-2xl border border-border bg-surface p-8 shadow-card">
        <h1 className="font-display text-2xl font-semibold text-foreground">Verify identity</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Enter the 6-digit code sent to your email. Expires in {minutes}:{seconds}
        </p>

        {error ? (
          <div className="mt-4 flex items-center gap-2 rounded-lg bg-error/10 p-3 text-sm text-error">
            <AlertCircle className="h-4 w-4 shrink-0" aria-hidden />
            {error}
          </div>
        ) : null}

        <div className="mt-6 flex justify-between gap-2">
          {otp.map((digit, index) => (
            <input
              key={index}
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(event) => updateDigit(index, event.target.value)}
              className="h-12 w-12 rounded-lg border border-input bg-background text-center text-lg focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
              aria-label={`Digit ${index + 1}`}
            />
          ))}
        </div>

        <button
          type="button"
          disabled={loading || otp.some((digit) => !digit)}
          onClick={handleVerify}
          className={cn(
            "mt-6 flex w-full items-center justify-center rounded-lg bg-accent px-4 py-3 text-sm font-semibold text-white",
            loading && "opacity-70",
          )}
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Verify"}
        </button>

        <button
          type="button"
          disabled={secondsLeft > 0}
          className="mt-3 w-full text-sm text-muted-foreground disabled:opacity-50"
        >
          Resend OTP {secondsLeft > 0 ? `(${minutes}:${seconds})` : ""}
        </button>

        <Link href="/login" className="mt-6 block text-center text-sm font-medium text-accent hover:underline">
          Use different account
        </Link>
      </div>
    </div>
  );
}

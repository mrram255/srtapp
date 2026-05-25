"use client";

import { useEffect, useState } from "react";

import { useRouter } from "next/navigation";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { useAuthStore } from "@/store/auth-store";

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const router = useRouter();
  const checkAuth = useAuthStore((s) => s.checkAuth);
  const [phase, setPhase] = useState<"checking" | "anon" | "authed">("checking");

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const ok = await checkAuth();
      if (cancelled) return;
      setPhase(ok ? "authed" : "anon");
      if (!ok) {
        router.replace("/login");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [checkAuth, router]);

  if (phase === "checking") {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="animate-pulse text-center">
          <div className="mx-auto mb-4 h-12 w-12 rounded-full bg-accent/20" />
          <div className="mx-auto h-4 w-32 rounded bg-muted" />
        </div>
      </div>
    );
  }

  if (phase !== "authed") {
    return null;
  }

  return <DashboardShell>{children}</DashboardShell>;
}

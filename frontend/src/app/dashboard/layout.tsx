"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { useAuthStore } from "@/store/auth-store";

export default function DashboardLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const router = useRouter();
  const hydrate = useAuthStore((s) => s.hydrate);
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  // If zustand already has persisted user (from localStorage), show immediately
  const [phase, setPhase] = useState<"checking" | "anon" | "authed">(
    isAuthenticated && user ? "authed" : "checking"
  );
  const startedRef = useRef(false);

  useEffect(() => {
    // Already authed from persisted store — still hydrate in background to refresh token
    if (isAuthenticated && user && phase === "authed") {
      void hydrate(); // background refresh, no spinner
      return;
    }

    if (startedRef.current) return;
    startedRef.current = true;
    let cancelled = false;

    void (async () => {
      const ok = await hydrate();
      if (cancelled) return;
      if (ok) {
        setPhase("authed");
      } else {
        setPhase("anon");
        router.replace("/login?reason=session");
      }
    })();

    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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

  if (phase !== "authed") return null;

  return <DashboardShell>{children}</DashboardShell>;
}

"use client";

import { useEffect, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

import { getDashboardPathForRole } from "@/lib/auth";
import { useAuthStore } from "@/stores/authStore";

type ProtectedRouteProps = {
  children: ReactNode;
  roles?: string[];
  fallback?: string;
  /** Defaults to the signed-in user's role home dashboard. */
  unauthorized?: string;
};

export function ProtectedRoute({
  children,
  roles,
  fallback = "/login",
  unauthorized,
}: ProtectedRouteProps) {
  const router = useRouter();
  const { isAuthenticated, user, hydrate, isLoading } = useAuthStore();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    let active = true;
    (async () => {
      if (!isAuthenticated) {
        const ok = await hydrate();
        if (!active) return;
        if (!ok) {
          router.replace(fallback);
          return;
        }
      }
      setChecking(false);
    })();
    return () => {
      active = false;
    };
  }, [fallback, hydrate, isAuthenticated, router]);

  if (checking || isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-accent" aria-label="Loading" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  if (roles && roles.length > 0 && !roles.includes(user.role)) {
    router.replace(unauthorized ?? getDashboardPathForRole(user.role, user.role_slug));
    return null;
  }

  return <>{children}</>;
}

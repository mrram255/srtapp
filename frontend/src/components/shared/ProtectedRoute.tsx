"use client";

import { useEffect, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

import { useAuthStore } from "@/stores/authStore";

type ProtectedRouteProps = {
  children: ReactNode;
  roles?: string[];
  fallback?: string;
  unauthorized?: string;
};

export function ProtectedRoute({
  children,
  roles,
  fallback = "/login",
  unauthorized = "/dashboard/forbidden",
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
    router.replace(unauthorized);
    return null;
  }

  return <>{children}</>;
}

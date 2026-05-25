"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { clearMemoryAccessToken } from "@/lib/api/auth-token";

export function LogoutButton() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function logout() {
    setLoading(true);
    try {
      await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
      clearMemoryAccessToken();
      router.push("/login");
      router.refresh();
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      type="button"
      onClick={logout}
      disabled={loading}
      className="text-muted-foreground underline-offset-4 hover:text-foreground hover:underline disabled:opacity-50"
    >
      {loading ? "Signing out…" : "Logout"}
    </button>
  );
}

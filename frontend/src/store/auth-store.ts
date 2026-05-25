import { create } from "zustand";
import { persist } from "zustand/middleware";

import { clearMemoryAccessToken, setMemoryAccessToken } from "@/lib/api/auth-token";
import type { AuthUser } from "@/types";

interface AuthState {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: AuthUser | null) => void;
  checkAuth: () => Promise<boolean>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isLoading: false,
      isAuthenticated: false,

      login: async (email: string, password: string) => {
        const response = await fetch("/api/auth/login", {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        let parsed: { ok?: boolean; message?: string; user?: AuthUser | null; access?: string } = {};
        try {
          parsed = (await response.json()) as typeof parsed;
        } catch {
          parsed = {};
        }

        if (!response.ok) {
          throw new Error(typeof parsed.message === "string" ? parsed.message : "Login failed.");
        }

        if (typeof parsed.access === "string") {
          setMemoryAccessToken(parsed.access);
        }

        const user = parsed.user ?? null;
        set({
          user,
          isAuthenticated: !!user,
          isLoading: false,
        });
      },

      logout: async () => {
        try {
          await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
        } catch {
          /* clear locally anyway */
        } finally {
          clearMemoryAccessToken();
          set({ user: null, isAuthenticated: false, isLoading: false });
        }
      },

      setUser: (user) => {
        set({ user, isAuthenticated: !!user, isLoading: false });
      },

      checkAuth: async () => {
        try {
          const response = await fetch("/api/auth/me", { credentials: "include" });
          if (!response.ok) {
            set({ user: null, isAuthenticated: false, isLoading: false });
            return false;
          }
          const body = (await response.json()) as { user?: AuthUser };
          const user = body.user;
          if (!user) {
            set({ user: null, isAuthenticated: false, isLoading: false });
            return false;
          }
          set({ user, isAuthenticated: true, isLoading: false });
          return true;
        } catch {
          set({ user: null, isAuthenticated: false, isLoading: false });
          return false;
        }
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    },
  ),
);

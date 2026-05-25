import { create } from "zustand";
import { persist } from "zustand/middleware";

import {
  getDashboardPathForRole,
  getUser,
  login as authLogin,
  logout as authLogout,
  refreshToken,
  verify2FA,
} from "@/lib/auth";
import { clearMemoryAccessToken, setMemoryAccessToken } from "@/lib/api/auth-token";
import type { AuthUser } from "@/types";

interface AuthState {
  user: AuthUser | null;
  tokens: { access: string; refresh: string } | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  pendingSessionKey: string | null;
  login: (email: string, password: string) => Promise<{ requires2fa: boolean; redirectTo: string | null }>;
  verify2fa: (otp: string) => Promise<string>;
  logout: () => Promise<void>;
  setUser: (user: AuthUser | null) => void;
  clearAuth: () => void;
  hydrate: () => Promise<boolean>;
  checkAuth: () => Promise<boolean>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      pendingSessionKey: null,

      login: async (email, password) => {
        set({ isLoading: true });
        try {
          const result = await authLogin(email, password);
          if (result.requires2fa) {
            set({
              pendingSessionKey: result.sessionKey ?? null,
              user: result.user,
              isAuthenticated: false,
              isLoading: false,
            });
            return { requires2fa: true, redirectTo: "/verify-2fa" };
          }

          if (!result.user) {
            throw new Error("Login succeeded but user profile was missing. Check API_ORIGIN / Django auth/me.");
          }

          set({
            user: result.user,
            tokens: result.access ? { access: result.access, refresh: "" } : null,
            isAuthenticated: true,
            pendingSessionKey: null,
            isLoading: false,
          });

          return {
            requires2fa: false,
            redirectTo: getDashboardPathForRole(result.user.role),
          };
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      verify2fa: async (otp) => {
        const sessionKey = get().pendingSessionKey;
        if (!sessionKey) {
          throw new Error("Session expired. Please sign in again.");
        }
        set({ isLoading: true });
        try {
          const result = await verify2FA(otp, sessionKey);
          if (!result.user) {
            throw new Error("Verification succeeded but user profile was missing.");
          }
          set({
            user: result.user,
            tokens: result.access ? { access: result.access, refresh: "" } : null,
            isAuthenticated: true,
            pendingSessionKey: null,
            isLoading: false,
          });
          return getDashboardPathForRole(result.user.role);
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: async () => {
        await authLogout();
        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
          pendingSessionKey: null,
          isLoading: false,
        });
      },

      setUser: (user) => {
        set({ user, isAuthenticated: !!user, isLoading: false });
      },

      clearAuth: () => {
        clearMemoryAccessToken();
        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
          pendingSessionKey: null,
          isLoading: false,
        });
      },

      hydrate: async () => {
        const persisted = get().user;

        try {
          const boot = await fetch("/api/auth/bootstrap", {
            method: "POST",
            credentials: "include",
            cache: "no-store",
          });
          if (boot.ok) {
            const body = (await boot.json()) as { access?: string };
            if (body.access) {
              setMemoryAccessToken(body.access);
            }
          }
        } catch {
          /* non-fatal */
        }

        const { user, status } = await getUser();

        if (status === "ok" && user) {
          set({ user, isAuthenticated: true, isLoading: false });
          return true;
        }

        if (status === "unavailable" && persisted) {
          set({ user: persisted, isAuthenticated: true, isLoading: false });
          return true;
        }

        if (status === "unauthorized") {
          const refreshed = await refreshToken();
          if (refreshed) {
            const retry = await getUser();
            if (retry.status === "ok" && retry.user) {
              set({ user: retry.user, isAuthenticated: true, isLoading: false });
              return true;
            }
          }
        }

        get().clearAuth();
        return false;
      },

      checkAuth: async () => get().hydrate(),
    }),
    {
      name: "auth-storage-v3",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        pendingSessionKey: state.pendingSessionKey,
      }),
    },
  ),
);

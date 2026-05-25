import { create } from "zustand";
import * as SecureStore from "expo-secure-store";
import { isAxiosError } from "axios";

import api from "@/lib/api";
import { ACCESS_KEY, REFRESH_KEY, USER_KEY } from "@/lib/secure-keys";
import type { ApiEnvelope, AuthBundle, AuthUser } from "@/lib/types";

interface AuthState {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  restoreSession: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  restoreSession: async () => {
    try {
      const userJson = await SecureStore.getItemAsync(USER_KEY);
      const token = await SecureStore.getItemAsync(ACCESS_KEY);

      if (userJson && token) {
        set({
          user: JSON.parse(userJson) as AuthUser,
          isAuthenticated: true,
          isLoading: false,
        });
      } else {
        set({ user: null, isAuthenticated: false, isLoading: false });
      }
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  login: async (email: string, password: string) => {
    if (!email.trim() || !password.trim()) {
      throw new Error("Email and password are required.");
    }

    try {
      const res = await api.post<ApiEnvelope<AuthBundle>>("/auth/login/", {
        email: email.trim(),
        password,
      });

      const bundle = res.data.data;
      if (!bundle?.access || !bundle?.refresh || !bundle?.user) {
        throw new Error(typeof res.data.message === "string" ? res.data.message : "Login failed.");
      }

      await SecureStore.setItemAsync(ACCESS_KEY, bundle.access);
      await SecureStore.setItemAsync(REFRESH_KEY, bundle.refresh);
      await SecureStore.setItemAsync(USER_KEY, JSON.stringify(bundle.user));

      set({
        user: bundle.user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (e) {
      if (isAxiosError(e)) {
        const base = api.defaults.baseURL ?? "";
        if (!e.response) {
          const isTimeout =
            e.code === "ECONNABORTED" || (e.message ?? "").toLowerCase().includes("timeout");
          if (isTimeout) {
            throw new Error(`API timeout (${base}). Is Django running on 0.0.0.0:8000?`);
          }
          throw new Error(
            `Cannot reach API (${base}). ${[String(e.code ?? ""), e.message].filter(Boolean).join(" — ")}`.trim() +
              ` Check Metro terminal for "[srtapp] → POST" URL; must match http://YOUR_IP:8000/api/v1/auth/login/.`,
          );
        }
        const msg = (e.response.data as ApiEnvelope<unknown> | undefined)?.message;
        throw new Error(typeof msg === "string" && msg.length > 0 ? msg : "Login failed.");
      }
      throw e instanceof Error ? e : new Error("Login failed.");
    }
  },

  logout: async () => {
    try {
      const refresh = await SecureStore.getItemAsync(REFRESH_KEY);
      if (refresh) {
        await api.post("/auth/logout/", { refresh });
      }
    } catch {
      /* still wipe local session */
    }

    await SecureStore.deleteItemAsync(ACCESS_KEY).catch(() => undefined);
    await SecureStore.deleteItemAsync(REFRESH_KEY).catch(() => undefined);
    await SecureStore.deleteItemAsync(USER_KEY).catch(() => undefined);
    try {
      const { clearBiometricCredentials } = await import("@/lib/biometric-auth");
      await clearBiometricCredentials();
    } catch {
      /* optional native module layer */
    }

    set({ user: null, isAuthenticated: false, isLoading: false });
  },
}));

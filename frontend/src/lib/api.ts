import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

import { clearMemoryAccessToken, getMemoryAccessToken, setMemoryAccessToken } from "@/lib/api/auth-token";

/** Browser hits Django directly; CORS allows any localhost dev port via regex in development.py */
function resolveApiBase(): string {
  return (
    process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
    process.env.API_ORIGIN?.replace(/\/$/, "") ??
    "http://localhost:8000/api/v1"
  );
}

const API_BASE = resolveApiBase();

export type ApiEnvelope<T = unknown> = {
  success: boolean;
  message: string;
  data?: T;
  errors?: Record<string, string[]>;
  error_code?: string;
  timestamp?: string;
};

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

api.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  let token = getMemoryAccessToken();
  if (!token && typeof window !== "undefined") {
    try {
      const boot = await fetch(`${window.location.origin}/api/auth/bootstrap`, {
        method: "POST",
        credentials: "include",
      });
      if (boot.ok) {
        const body = (await boot.json()) as { access?: string };
        if (body.access) {
          setMemoryAccessToken(body.access);
          token = body.access;
        }
      }
    } catch {
      /* ignore */
    }
  }
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  if (typeof window === "undefined") return null;

  const response = await fetch("/api/auth/refresh", {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    clearMemoryAccessToken();
    return null;
  }

  const body = (await response.json()) as { access?: string };
  if (body.access) {
    setMemoryAccessToken(body.access);
    return body.access;
  }
  return null;
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true;
      refreshPromise ??= refreshAccessToken().finally(() => {
        refreshPromise = null;
      });
      const token = await refreshPromise;
      if (token) {
        original.headers.Authorization = `Bearer ${token}`;
        return api(original);
      }
    }
    return Promise.reject(error);
  },
);

export function getApiErrorMessage(error: unknown, fallback = "Something went wrong."): string {
  if (axios.isAxiosError(error)) {
    if (error.code === "ERR_NETWORK") {
      return "Cannot reach the API server. Ensure Django is running on port 8000 and CORS is enabled for your frontend port.";
    }
    const data = error.response?.data as ApiEnvelope | undefined;
    if (data?.message) return data.message;
    if (error.response?.status === 401) return "Session expired. Please sign in again.";
    if (error.response?.status === 403) return "You do not have permission to perform this action.";
  }
  if (error instanceof Error) return error.message;
  return fallback;
}

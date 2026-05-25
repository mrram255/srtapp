/**
 * Axios API client — production-safe.
 *
 * Server-side  → calls Django directly via API_ORIGIN (server-to-server, no CORS)
 * Browser-side → calls Next.js /django-api/ proxy (never exposes backend URL)
 *
 * This means the same code works in dev, staging, and production
 * without any environment variable changes after deployment.
 */
import axios, {
  AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";

import {
  clearMemoryAccessToken,
  getMemoryAccessToken,
  setMemoryAccessToken,
} from "@/lib/api/auth-token";

// ─── Base URLs ────────────────────────────────────────────────────────────────

/** Server-side: direct Django call (no CORS, fastest path) */
const SERVER_BASE =
  (process.env.API_ORIGIN ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1")
    .replace(/\/$/, "");

/**
 * Browser-side: always use Next.js proxy path.
 * /django-api/ is rewritten to Django by next.config.ts → no CORS, no exposed backend URL,
 * works identically in dev and production.
 */
const BROWSER_BASE = "/django-api";

// ─── Axios instance ───────────────────────────────────────────────────────────

const api: AxiosInstance = axios.create({
  baseURL: typeof window === "undefined" ? SERVER_BASE : BROWSER_BASE,
  timeout: 15_000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
  },
});

// ─── Helpers ──────────────────────────────────────────────────────────────────

function getCookieValue(name: string): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
  return match ? decodeURIComponent(match[2]) : null;
}

async function fetchAccessTokenFromBootstrap(): Promise<string | null> {
  try {
    const res = await fetch("/api/auth/bootstrap", {
      method: "POST",
      credentials: "include",
    });
    if (!res.ok) return null;
    const body = (await res.json()) as { access?: string };
    return typeof body.access === "string" ? body.access : null;
  } catch {
    return null;
  }
}

// ─── Request interceptor ──────────────────────────────────────────────────────

api.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  if (typeof window === "undefined") return config;

  // CSRF for mutating requests
  if (["post", "put", "patch", "delete"].includes(String(config.method ?? "").toLowerCase())) {
    const csrf = getCookieValue("csrftoken");
    if (csrf) config.headers["X-CSRFToken"] = csrf;
  }

  // Bearer token — memory first, then bootstrap
  let bearer = getMemoryAccessToken();
  if (!bearer) {
    bearer = await fetchAccessTokenFromBootstrap();
    if (bearer) setMemoryAccessToken(bearer);
  }
  if (bearer) config.headers.Authorization = `Bearer ${bearer}`;

  return config;
});

// ─── Response interceptor — silent 401 → refresh → retry ────────────────────

type RetryConfig = InternalAxiosRequestConfig & { _retry?: boolean };

let isRefreshing = false;
let pendingQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

function flushQueue(error: Error | null) {
  pendingQueue.forEach((p) => (error ? p.reject(error) : p.resolve()));
  pendingQueue = [];
}

api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as RetryConfig | undefined;
    if (!original) return Promise.reject(error);

    // Never retry refresh calls — avoids infinite loop
    if ((original.url ?? "").includes("/auth/refresh")) return Promise.reject(error);

    if (error.response?.status === 401 && !original._retry && typeof window !== "undefined") {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingQueue.push({ resolve, reject });
        })
          .then(() => api(original))
          .catch((e) => Promise.reject(e));
      }

      original._retry = true;
      isRefreshing = true;

      try {
        const res = await axios.post<{ access?: string }>(
          "/api/auth/refresh",
          {},
          { withCredentials: true },
        );
        const token = res.data.access;
        if (typeof token === "string") setMemoryAccessToken(token);
        flushQueue(null);
        return api(original);
      } catch (refreshErr) {
        flushQueue(refreshErr instanceof Error ? refreshErr : new Error("Refresh failed"));
        clearMemoryAccessToken();
        window.location.href = "/login";
        return Promise.reject(refreshErr);
      } finally {
        isRefreshing = false;
      }
    }

    // Normalize error message
    const data = error.response?.data as { message?: string } | undefined;
    const msg =
      typeof data?.message === "string" && data.message.length > 0
        ? data.message
        : "Something went wrong.";
    return Promise.reject(new Error(msg));
  },
);

export default api;
export { api };
/** @deprecated use default export `api` */
export const apiClient = api;

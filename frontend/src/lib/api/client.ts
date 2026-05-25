import axios, { AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from "axios";

import { clearMemoryAccessToken, getMemoryAccessToken, setMemoryAccessToken } from "@/lib/api/auth-token";

const serverBaseURL =
  process.env.API_ORIGIN ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

const browserBaseURL =
  typeof window !== "undefined"
    ? (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1").replace(/\/$/, "")
    : "";

const api: AxiosInstance = axios.create({
  baseURL: typeof window === "undefined" ? serverBaseURL : browserBaseURL || undefined,
  timeout: 15000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
  },
});

function getCookieValue(name: string): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
  return match ? decodeURIComponent(match[2]) : null;
}

api.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  if (typeof window !== "undefined") {
    if (["post", "put", "patch", "delete"].includes(String(config.method ?? "").toLowerCase())) {
      const csrf = getCookieValue("csrftoken");
      if (csrf) {
        config.headers["X-CSRFToken"] = csrf;
      }
    }

    let bearer = getMemoryAccessToken();
    if (!bearer) {
      try {
        const origin = window.location.origin;
        const boot = await fetch(`${origin}/api/auth/bootstrap`, {
          method: "POST",
          credentials: "include",
        });
        if (boot.ok) {
          const body = (await boot.json()) as { access?: string };
          if (typeof body.access === "string") {
            setMemoryAccessToken(body.access);
            bearer = body.access;
          }
        }
      } catch {
        /* ignore */
      }
    }

    if (bearer) {
      config.headers.Authorization = `Bearer ${bearer}`;
    }
  }

  return config;
});

type RetryConfig = InternalAxiosRequestConfig & { _retry?: boolean };

let isRefreshing = false;
let failedQueue: Array<{ resolve: (v?: unknown) => void; reject: (r?: unknown) => void }> = [];

function processQueue(error: Error | null) {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error);
    else prom.resolve();
  });
  failedQueue = [];
}

api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryConfig | undefined;

    if (!originalRequest) {
      return Promise.reject(error);
    }

    const url = originalRequest.url ?? "";
    if (url.includes("/api/auth/refresh")) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (typeof window !== "undefined") {
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          })
            .then(() => api(originalRequest))
            .catch((err) => Promise.reject(err));
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
          const refreshRes = await axios.post<{ access?: string }>(
            `${window.location.origin}/api/auth/refresh`,
            {},
            { withCredentials: true },
          );
          const nextAccess = refreshRes.data.access;
          if (typeof nextAccess === "string") {
            setMemoryAccessToken(nextAccess);
          }
          processQueue(null);
          return api(originalRequest);
        } catch (refreshError) {
          processQueue(refreshError instanceof Error ? refreshError : new Error("Refresh failed"));
          clearMemoryAccessToken();
          window.location.href = "/login";
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }
    }

    const data = error.response?.data as { message?: string } | undefined;
    const msg = typeof data?.message === "string" && data.message.length > 0 ? data.message : "Something went wrong.";
    return Promise.reject(new Error(msg));
  },
);

export default api;

/** @deprecated Use default export `api` */
export const apiClient = api;

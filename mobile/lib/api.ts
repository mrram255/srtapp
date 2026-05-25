import axios, {
  AxiosHeaders,
  type AxiosError,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from "axios";
import * as SecureStore from "expo-secure-store";

import { phoneLikelyCannotReachApiUrl } from "@/lib/dev-api-url-guard";
import { ACCESS_KEY, REFRESH_KEY } from "@/lib/secure-keys";
import type { ApiEnvelope } from "@/lib/types";

type RetryConfig = InternalAxiosRequestConfig & { _retry?: boolean };

type QueueItem = {
  resolve: (value: AxiosResponse<unknown>) => void;
  reject: (reason?: unknown) => void;
  config: RetryConfig;
};

const baseURL = (process.env.EXPO_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1").replace(/\/$/, "");

if (typeof __DEV__ !== "undefined" && __DEV__) {
  const unreachable = phoneLikelyCannotReachApiUrl(baseURL);
  if (unreachable) {
    // eslint-disable-next-line no-console -- dev troubleshooting only
    console.error(
      "\n========== [SRTAPP mobile] BAD API URL ==========\n" +
        unreachable +
        "\n\nBundled URL: " +
        baseURL +
        "\nFix: mobile/.env → EXPO_PUBLIC_API_URL=http://<Wi‑Fi IPv4>:8000/api/v1 (Windows ipconfig), then restart Metro with -c." +
        "\n=================================================\n",
    );
  }
  // eslint-disable-next-line no-console -- dev troubleshooting only
  console.warn("[srtapp] Axios baseURL =", baseURL);
}

const api = axios.create({
  baseURL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

function extractAxiosMessage(error: AxiosError): string {
  const data = error.response?.data as ApiEnvelope<unknown> | undefined;
  if (typeof data?.message === "string" && data.message.length > 0) return data.message;
  return error.message.length > 0 ? error.message : "Something went wrong.";
}

api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync(ACCESS_KEY);
  if (token) {
    config.headers = AxiosHeaders.from(config.headers ?? {});
    config.headers.set("Authorization", `Bearer ${token}`);
  }
  if (typeof __DEV__ !== "undefined" && __DEV__) {
    const u = `${config.baseURL ?? ""}${config.url ?? ""}`;
    // eslint-disable-next-line no-console -- dev troubleshooting only
    console.warn("[srtapp] →", String(config.method ?? "GET").toUpperCase(), u);
  }
  return config;
});

let isRefreshing = false;
let queue: QueueItem[] = [];

function flushFailure(reason: Error) {
  const pending = queue;
  queue = [];
  pending.forEach(({ reject }) => reject(reason));
}

/** 401 on these routes must not trigger refresh (would hide real errors like wrong password). */
function shouldBypassJwtRefresh401(config: RetryConfig): boolean {
  const rel = `${config.url ?? ""}`.toLowerCase();
  return rel.includes("/auth/login") || rel.includes("/auth/token/refresh");
}

function flushSuccess(access: string) {
  const pending = queue;
  queue = [];
  pending.forEach(({ resolve, reject, config }) => {
    try {
      config.headers = AxiosHeaders.from(config.headers ?? {});
      config.headers.set("Authorization", `Bearer ${access}`);
      void api(config).then(resolve).catch(reject);
    } catch (e) {
      reject(e);
    }
  });
}

api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as RetryConfig | undefined;
    if (!original) {
      return Promise.reject(new Error(extractAxiosMessage(error)));
    }

    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(new Error(extractAxiosMessage(error)));
    }

    if (shouldBypassJwtRefresh401(original)) {
      return Promise.reject(new Error(extractAxiosMessage(error)));
    }

    if (isRefreshing) {
      return new Promise<AxiosResponse<unknown>>((resolve, reject) => {
        queue.push({ resolve, reject, config: original });
      });
    }

    original._retry = true;
    isRefreshing = true;

    try {
      const refresh = await SecureStore.getItemAsync(REFRESH_KEY);
      if (!refresh) {
        throw new Error("Session expired. Please login again.");
      }

      const res = await axios.post<ApiEnvelope<{ access?: string; refresh?: string }>>(
        `${baseURL}/auth/token/refresh/`,
        { refresh },
        {
          headers: { "Content-Type": "application/json", Accept: "application/json" },
        },
      );

      const access = res.data?.data?.access;
      const rotatedRefresh = res.data?.data?.refresh;

      if (!access || res.data.success === false) {
        throw new Error(
          typeof res.data.message === "string" && res.data.message.length > 0
            ? res.data.message
            : "Session expired. Please login again.",
        );
      }

      await SecureStore.setItemAsync(ACCESS_KEY, access);
      if (rotatedRefresh) {
        await SecureStore.setItemAsync(REFRESH_KEY, rotatedRefresh);
      }

      flushSuccess(access);

      original.headers = AxiosHeaders.from(original.headers ?? {});
      original.headers.set("Authorization", `Bearer ${access}`);
      return api(original);
    } catch (e) {
      const err = e instanceof Error ? e : new Error("Session expired. Please login again.");
      flushFailure(err);
      await SecureStore.deleteItemAsync(ACCESS_KEY).catch(() => undefined);
      await SecureStore.deleteItemAsync(REFRESH_KEY).catch(() => undefined);
      return Promise.reject(err);
    } finally {
      isRefreshing = false;
    }
  },
);

export default api;

export async function getToken(): Promise<string | null> {
  return SecureStore.getItemAsync(ACCESS_KEY);
}

export async function removeTokens(): Promise<void> {
  await Promise.all([
    SecureStore.deleteItemAsync(ACCESS_KEY).catch(() => undefined),
    SecureStore.deleteItemAsync(REFRESH_KEY).catch(() => undefined),
  ]);
}

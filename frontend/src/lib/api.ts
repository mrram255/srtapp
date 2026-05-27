/**
 * api.ts — canonical re-export hub.
 * All imports from "@/lib/api" get the proxy-safe axios client.
 * Browser → /django-api/ proxy → Django (never direct)
 * Server → Django direct (server-to-server, no CORS)
 */
import { default as axiosApi } from "@/lib/api/client";
export { default as api, apiClient } from "@/lib/api/client";
export type { ApiEnvelope } from "@/lib/api/types";

export function getApiErrorMessage(error: unknown, fallback = "Something went wrong."): string {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { default: axios } = require("axios") as typeof import("axios");
  if (axios.isAxiosError(error)) {
    if (error.code === "ERR_NETWORK") return "Cannot reach the server. Please try again.";
    const data = error.response?.data as { message?: string } | undefined;
    if (data?.message) return data.message;
    if (error.response?.status === 401) return "Session expired. Please sign in again.";
    if (error.response?.status === 403) return "You do not have permission to perform this action.";
  }
  if (error instanceof Error) return error.message;
  return fallback;
}

export default axiosApi;

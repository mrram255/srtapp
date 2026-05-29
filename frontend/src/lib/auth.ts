import { api, type ApiEnvelope } from "@/lib/api";
import { clearMemoryAccessToken, setMemoryAccessToken } from "@/lib/api/auth-token";
import { resolveDashboardPath } from "@/lib/auth/role-routes";
import type { AuthUser } from "@/types";

export type LoginResult = {
  requires2fa: boolean;
  sessionKey?: string;
  user: AuthUser | null;
  access?: string;
  refresh?: string;
};

export type AuthTokens = {
  access: string;
  refresh: string;
};

function normalizeUser(raw: Record<string, unknown> | null | undefined): AuthUser | null {
  if (!raw) return null;
  return {
    id: String(raw.id ?? ""),
    email: String(raw.email ?? ""),
    role: String(raw.role ?? "").toUpperCase(),
    role_slug: raw.role_slug ? String(raw.role_slug) : null,
    first_name: String(raw.first_name ?? ""),
    last_name: String(raw.last_name ?? ""),
    college_id: raw.college_id ? String(raw.college_id) : null,
    department_id: raw.department_id ? String(raw.department_id) : null,
    is_verified: Boolean(raw.is_verified),
    must_change_password: Boolean(raw.must_change_password),
    profile_photo: String(raw.profile_photo ?? ""),
    signature: String(raw.signature ?? ""),
  };
}

export async function login(email: string, password: string): Promise<LoginResult> {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
  });

  const body = (await response.json()) as {
    message?: string;
    access?: string;
    user?: Record<string, unknown> | null;
    requires2fa?: boolean;
    sessionKey?: string;
  };

  if (!response.ok) {
    const hint =
      response.status === 502
        ? " Django backend is not running. Start it: cd ~/srtapp/backend && python manage.py runserver"
        : "";
    throw new Error((body.message ?? "Login failed.") + hint);
  }

  if (body.requires2fa) {
    return {
      requires2fa: true,
      sessionKey: body.sessionKey,
      user: normalizeUser(body.user),
    };
  }

  if (body.access) {
    setMemoryAccessToken(body.access);
  }

  return {
    requires2fa: false,
    user: normalizeUser(body.user),
    access: body.access,
  };
}

export async function verify2FA(otpCode: string, sessionKey: string): Promise<LoginResult> {
  const response = await fetch("/api/auth/verify-2fa", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ otp_code: otpCode, session_key: sessionKey }),
  });

  const body = (await response.json()) as {
    message?: string;
    access?: string;
    user?: Record<string, unknown> | null;
  };

  if (!response.ok) {
    throw new Error(body.message ?? "Verification failed.");
  }

  if (body.access) {
    setMemoryAccessToken(body.access);
  }

  return {
    requires2fa: false,
    user: normalizeUser(body.user),
    access: body.access,
  };
}

export async function logout(): Promise<void> {
  try {
    await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
  } finally {
    clearMemoryAccessToken();
  }
}

export async function refreshToken(): Promise<string | null> {
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

export type GetUserResult = {
  user: AuthUser | null;
  status: "ok" | "unauthorized" | "unavailable";
};

export async function getUser(): Promise<GetUserResult> {
  const fetchMe = async () => {
    const response = await fetch("/api/auth/me", { credentials: "include", cache: "no-store" });
    if (response.status === 401 || response.status === 403) {
      return { user: null, status: "unauthorized" as const };
    }
    if (!response.ok) {
      return { user: null, status: "unavailable" as const };
    }
    const body = (await response.json()) as { user?: Record<string, unknown> };
    const user = normalizeUser(body.user);
    if (!user) {
      return { user: null, status: "unauthorized" as const };
    }
    return { user, status: "ok" as const };
  };

  let result = await fetchMe();
  if (result.status === "unauthorized") {
    const access = await refreshToken();
    if (access) {
      result = await fetchMe();
    }
  }
  return result;
}

export function isAuthenticated(user: AuthUser | null): boolean {
  return !!user;
}

export function hasRole(user: AuthUser | null, role: string): boolean {
  return user?.role === role;
}

export function hasPermission(user: AuthUser | null, module: string, action: string): boolean {
  void user;
  void module;
  void action;
  return true;
}

export function getDashboardPathForRole(role: string, roleSlug?: string | null): string {
  return resolveDashboardPath(role, roleSlug);
}

export async function requestPasswordReset(email: string): Promise<string> {
  const { data } = await api.post<ApiEnvelope>("/auth/password/reset/", { email });
  return data.message;
}

export async function confirmPasswordReset(payload: {
  email: string;
  otp_code: string;
  new_password: string;
  confirm_password: string;
}): Promise<string> {
  const { data } = await api.post<ApiEnvelope>("/auth/password/reset/confirm/", payload);
  return data.message;
}

export { normalizeUser };

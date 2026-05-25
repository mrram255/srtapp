import { api, type ApiEnvelope } from "@/lib/api";
import { clearMemoryAccessToken, setMemoryAccessToken } from "@/lib/api/auth-token";
import { ROLE_HOME_SEGMENT } from "@/lib/auth/constants";
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
    role: String(raw.role ?? ""),
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
    body: JSON.stringify({ email, password }),
  });

  const body = (await response.json()) as {
    message?: string;
    access?: string;
    user?: AuthUser | null;
    requires2fa?: boolean;
    sessionKey?: string;
  };

  if (!response.ok) {
    throw new Error(body.message ?? "Login failed.");
  }

  if (body.requires2fa) {
    return {
      requires2fa: true,
      sessionKey: body.sessionKey,
      user: body.user ?? null,
    };
  }

  if (body.access) {
    setMemoryAccessToken(body.access);
  }

  return {
    requires2fa: false,
    user: body.user ?? null,
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
    user?: AuthUser | null;
  };

  if (!response.ok) {
    throw new Error(body.message ?? "Verification failed.");
  }

  if (body.access) {
    setMemoryAccessToken(body.access);
  }

  return {
    requires2fa: false,
    user: body.user ?? null,
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
  const response = await fetch("/api/auth/refresh", { method: "POST", credentials: "include" });
  if (!response.ok) return null;
  const body = (await response.json()) as { access?: string };
  if (body.access) {
    setMemoryAccessToken(body.access);
    return body.access;
  }
  return null;
}

export async function getUser(): Promise<AuthUser | null> {
  const response = await fetch("/api/auth/me", { credentials: "include" });
  if (!response.ok) return null;
  const body = (await response.json()) as { user?: AuthUser };
  return body.user ?? null;
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

export function getDashboardPathForRole(role: string): string {
  const segment = ROLE_HOME_SEGMENT[role] ?? "student";
  return `/dashboard/${segment}`;
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

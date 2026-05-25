import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { ACCESS_COOKIE, REFRESH_COOKIE } from "@/lib/auth/constants";
import { verifyAccessToken } from "@/lib/auth/jwt";

export type RefreshSessionResult = {
  response: NextResponse;
  access: string | null;
};

/** Try to rotate access token — calls Django DIRECTLY (no middleware loop). */
export async function refreshSessionCookies(
  request: NextRequest,
): Promise<RefreshSessionResult | null> {
  const refreshToken = request.cookies.get(REFRESH_COOKIE)?.value;
  if (!refreshToken) return null;

  try {
    const apiBase =
      process.env.API_ORIGIN ??
      process.env.NEXT_PUBLIC_API_URL ??
      "http://localhost:8000/api/v1";

    const refreshUrl = `${apiBase.replace(/\/$/, "")}/auth/refresh/`;

    const upstream = await fetch(refreshUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: refreshToken }),
      cache: "no-store",
    });

    if (!upstream.ok) return null;

    const payload = (await upstream.json()) as {
      success?: boolean;
      data?: { access?: string; refresh?: string };
    };

    const access = payload.data?.access;
    const rotatedRefresh = payload.data?.refresh;

    if (!access) return null;

    const secure = process.env.NODE_ENV === "production";
    const continuation = NextResponse.next({ request });

    continuation.cookies.set(ACCESS_COOKIE, access, {
      httpOnly: true,
      secure,
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 15,
    });

    if (rotatedRefresh) {
      continuation.cookies.set(REFRESH_COOKIE, rotatedRefresh, {
        httpOnly: true,
        secure,
        sameSite: "lax",
        path: "/",
        maxAge: 60 * 60 * 24 * 7,
      });
    }

    return { response: continuation, access };
  } catch {
    return null;
  }
}

export async function resolveSessionFromRequest(request: NextRequest) {
  const access = request.cookies.get(ACCESS_COOKIE)?.value;
  if (access) {
    const session = await verifyAccessToken(access);
    if (session) return { session, access };
  }

  const refreshed = await refreshSessionCookies(request);
  if (!refreshed?.access) return { session: null, access: null, refreshed: null };

  const session = await verifyAccessToken(refreshed.access);
  return { session, access: refreshed.access, refreshed: refreshed.response };
}

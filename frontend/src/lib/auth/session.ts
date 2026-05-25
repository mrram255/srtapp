import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { ACCESS_COOKIE, REFRESH_COOKIE } from "@/lib/auth/constants";
import { verifyAccessToken } from "@/lib/auth/jwt";

export type RefreshSessionResult = {
  response: NextResponse;
  access: string | null;
};

/** Try to rotate access token via Next refresh route (middleware-safe). */
export async function refreshSessionCookies(
  request: NextRequest,
): Promise<RefreshSessionResult | null> {
  if (!request.cookies.get(REFRESH_COOKIE)?.value) {
    return null;
  }

  try {
    const refreshUrl = new URL("/api/auth/refresh", request.url);
    const upstream = await fetch(refreshUrl, {
      method: "POST",
      headers: {
        cookie: request.headers.get("cookie") ?? "",
      },
      cache: "no-store",
    });

    if (!upstream.ok) {
      return null;
    }

    const body = (await upstream.json()) as { access?: string };
    const continuation = NextResponse.next({ request });
    const setCookies =
      typeof upstream.headers.getSetCookie === "function"
        ? upstream.headers.getSetCookie()
        : [];

    for (const header of setCookies) {
      continuation.headers.append("set-cookie", header);
    }

    return { response: continuation, access: body.access ?? null };
  } catch {
    return null;
  }
}

export async function resolveSessionFromRequest(request: NextRequest) {
  const access = request.cookies.get(ACCESS_COOKIE)?.value;
  if (access) {
    const session = await verifyAccessToken(access);
    if (session) {
      return { session, access };
    }
  }

  const refreshed = await refreshSessionCookies(request);
  if (!refreshed?.access) {
    return { session: null, access: null, refreshed: null };
  }

  const session = await verifyAccessToken(refreshed.access);
  return { session, access: refreshed.access, refreshed: refreshed.response };

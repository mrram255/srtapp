import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import {
  ACCESS_COOKIE,
  DASHBOARD_SEGMENT_ROLES,
  REFRESH_COOKIE,
  ROLE_HOME_SEGMENT,
  type Role,
} from "@/lib/auth/constants";
import { verifyAccessToken } from "@/lib/auth/jwt";

function normalizePathname(pathname: string) {
  if (pathname === "/") return "/";
  return pathname.replace(/\/+$/, "") || "/";
}

const PUBLIC_PREFIXES = [
  "/login",
  "/forgot-password",
  "/register",
  "/reset-password",
  "/api/",
  "/_next",
  "/public",
];

const PUBLIC_EXACT = new Set(["/", "/favicon.ico", "/health"]);

function isPublic(normalizedPath: string, rawPath: string) {
  if (PUBLIC_EXACT.has(normalizedPath)) return true;
  return PUBLIC_PREFIXES.some((prefix) => rawPath.startsWith(prefix));
}

function isStaticAsset(pathname: string) {
  return /\.(js|css|svg|png|jpg|jpeg|gif|webp|ico|woff|woff2|ttf|otf|eot)$/.test(pathname);
}

export async function middleware(request: NextRequest) {
  const pathname = normalizePathname(request.nextUrl.pathname);

  if (isStaticAsset(request.nextUrl.pathname)) {
    return NextResponse.next();
  }

  if (pathname.startsWith("/login")) {
    const token = request.cookies.get(ACCESS_COOKIE)?.value;
    if (token) {
      const session = await verifyAccessToken(token);
      if (session) {
        return NextResponse.redirect(new URL("/dashboard", request.url));
      }
    }
    return NextResponse.next();
  }

  if (isPublic(pathname, request.nextUrl.pathname)) {
    return NextResponse.next();
  }

  const token = request.cookies.get(ACCESS_COOKIE)?.value;
  if (!token) {
    const login = new URL("/login", request.url);
    login.searchParams.set("next", pathname);
    return NextResponse.redirect(login);
  }

  const session = await verifyAccessToken(token);
  if (!session) {
    const login = new URL("/login", request.url);
    login.searchParams.set("next", pathname);
    const res = NextResponse.redirect(login);
    res.cookies.delete(ACCESS_COOKIE);
    res.cookies.delete(REFRESH_COOKIE);
    return res;
  }

  const res = NextResponse.next();
  res.headers.set("x-user-id", session.userId);
  res.headers.set("x-user-role", session.role);
  res.headers.set("x-college-id", session.collegeId ?? "");

  if (!pathname.startsWith("/dashboard")) {
    return res;
  }

  if (pathname === "/dashboard") {
    return res;
  }

  if (pathname.startsWith("/dashboard/forbidden")) {
    return res;
  }

  const match = pathname.match(/^\/dashboard\/([^/]+)/);
  if (!match) {
    return res;
  }

  const segment = match[1];
  const allowed = DASHBOARD_SEGMENT_ROLES[segment];
  if (!allowed || !allowed.includes(session.role as Role)) {
    const homeSegment = ROLE_HOME_SEGMENT[session.role] ?? "student";
    return NextResponse.redirect(new URL(`/dashboard/${homeSegment}`, request.url));
  }

  return res;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { ACCESS_COOKIE, REFRESH_COOKIE } from "@/lib/auth/constants";

type DjangoEnvelope = {
  success?: boolean;
  message?: string;
  data?: {
    access?: string;
    refresh?: string;
  };
};

export async function POST(request: Request) {
  let refreshFromBody: string | undefined;
  try {
    const json = (await request.json()) as { refresh?: unknown };
    refreshFromBody = typeof json.refresh === "string" ? json.refresh : undefined;
  } catch {
    refreshFromBody = undefined;
  }

  const cookieStore = await cookies();
  const refreshToken = cookieStore.get(REFRESH_COOKIE)?.value ?? refreshFromBody;

  if (!refreshToken) {
    return NextResponse.json({ message: "No refresh token." }, { status: 401 });
  }

  const apiBase =
    process.env.API_ORIGIN ??
    process.env.NEXT_PUBLIC_API_URL ??
    "http://localhost:8000/api/v1";

  const refreshUrl = `${apiBase.replace(/\/$/, "")}/auth/refresh/`;

  const upstream = await fetch(refreshUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: refreshToken }),
  });

  let payload: DjangoEnvelope;
  try {
    payload = (await upstream.json()) as DjangoEnvelope;
  } catch {
    return NextResponse.json({ message: "Unexpected response from auth server." }, { status: 502 });
  }

  const access = payload.data?.access;
  const rotatedRefresh = payload.data?.refresh;
  const ok = upstream.ok && payload.success !== false && access;

  if (!ok) {
    const res = NextResponse.json(
      {
        message:
          typeof payload.message === "string" && payload.message.length > 0
            ? payload.message
            : "Refresh failed.",
      },
      { status: upstream.status >= 400 ? upstream.status : 401 },
    );
    res.cookies.delete(ACCESS_COOKIE);
    res.cookies.delete(REFRESH_COOKIE);
    return res;
  }

  const secure = process.env.NODE_ENV === "production";

  const res = NextResponse.json({ ok: true, access });

  res.cookies.set(ACCESS_COOKIE, access!, {
    httpOnly: true,
    secure,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 15,
  });

  if (rotatedRefresh) {
    res.cookies.set(REFRESH_COOKIE, rotatedRefresh, {
      httpOnly: true,
      secure,
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24 * 7,
    });
  }

  return res;
}

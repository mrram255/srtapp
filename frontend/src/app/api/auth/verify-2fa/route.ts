import { NextResponse } from "next/server";

import { ACCESS_COOKIE, REFRESH_COOKIE } from "@/lib/auth/constants";

type DjangoEnvelope = {
  success?: boolean;
  message?: string;
  data?: {
    access?: string;
    refresh?: string;
    user?: unknown;
  };
};

export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ message: "Invalid JSON body." }, { status: 400 });
  }

  const otp_code =
    typeof body === "object" && body !== null && "otp_code" in body
      ? String((body as { otp_code?: unknown }).otp_code ?? "")
      : "";
  const session_key =
    typeof body === "object" && body !== null && "session_key" in body
      ? String((body as { session_key?: unknown }).session_key ?? "")
      : "";

  if (!otp_code || !session_key) {
    return NextResponse.json({ message: "OTP and session are required." }, { status: 400 });
  }

  const apiBase =
    process.env.API_ORIGIN ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

  const upstream = await fetch(`${apiBase.replace(/\/$/, "")}/auth/verify-2fa/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ otp_code, session_key }),
  });

  let payload: DjangoEnvelope;
  try {
    payload = (await upstream.json()) as DjangoEnvelope;
  } catch {
    return NextResponse.json({ message: "Unexpected response from auth server." }, { status: 502 });
  }

  const tokens = payload.data;
  const ok = upstream.ok && payload.success !== false && tokens?.access && tokens?.refresh;

  if (!ok) {
    const message =
      typeof payload.message === "string" && payload.message.length > 0
        ? payload.message
        : "Verification failed.";
    return NextResponse.json({ message }, { status: upstream.status >= 400 ? upstream.status : 400 });
  }

  const secure = process.env.NODE_ENV === "production";
  const res = NextResponse.json({
    ok: true,
    user: tokens.user ?? null,
    access: tokens.access,
  });

  res.cookies.set(ACCESS_COOKIE, tokens.access!, {
    httpOnly: true,
    secure,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 15,
  });

  res.cookies.set(REFRESH_COOKIE, tokens.refresh!, {
    httpOnly: true,
    secure,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });

  return res;
}

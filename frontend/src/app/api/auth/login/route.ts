import { NextResponse } from "next/server";

import { ACCESS_COOKIE, REFRESH_COOKIE } from "@/lib/auth/constants";

type DjangoEnvelope = {
  success?: boolean;
  message?: string;
  data?: {
    access?: string;
    refresh?: string;
    user?: unknown;
    user_data?: unknown;
    requires_2fa?: boolean;
    session_key?: string;
  };
};

export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ message: "Invalid JSON body." }, { status: 400 });
  }

  let authLoginUrl = "";
  try {
    const email =
      typeof body === "object" && body !== null && "email" in body
        ? String((body as { email?: unknown }).email ?? "")
        : "";
    const password =
      typeof body === "object" && body !== null && "password" in body
        ? String((body as { password?: unknown }).password ?? "")
        : "";

    if (!email || !password) {
      return NextResponse.json({ message: "Email and password required." }, { status: 400 });
    }

    const apiBase =
      process.env.API_ORIGIN ??
      process.env.NEXT_PUBLIC_API_URL ??
      "http://localhost:8000/api/v1";

    authLoginUrl = `${apiBase.replace(/\/$/, "")}/auth/login/`;

    const upstream = await fetch(authLoginUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    let payload: DjangoEnvelope;
    try {
      payload = (await upstream.json()) as DjangoEnvelope;
    } catch {
      return NextResponse.json({ message: "Unexpected response from auth server." }, { status: 502 });
    }

    const tokens = payload.data;

    if (upstream.ok && payload.success !== false && tokens?.requires_2fa) {
      return NextResponse.json({
        ok: true,
        requires2fa: true,
        sessionKey: tokens.session_key,
        user: tokens.user_data ?? tokens.user ?? null,
        message: payload.message,
      });
    }

    const ok = upstream.ok && payload.success !== false && tokens?.access && tokens?.refresh;

    if (!ok) {
      const status = upstream.status >= 400 ? upstream.status : 401;
      const message =
        typeof payload.message === "string" && payload.message.length > 0
          ? payload.message
          : "Login failed.";
      return NextResponse.json({ message }, { status });
    }

    const secure = process.env.NODE_ENV === "production";

    const rawUser = (tokens.user ?? tokens.user_data) as Record<string, unknown> | null | undefined;
    const user =
      rawUser && typeof rawUser === "object"
        ? { ...rawUser, role: String(rawUser.role ?? "").toUpperCase() }
        : null;

    const res = NextResponse.json({
      ok: true,
      user,
      /** Mirrors cookie for Authorization headers on Django requests (also stored httpOnly). */
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
  } catch (err) {
    const causeCode =
      err instanceof Error && err.cause && typeof err.cause === "object" && "code" in err.cause
        ? String((err.cause as { code?: unknown }).code ?? "")
        : "";
    const isFetchNetworkFailure =
      err instanceof TypeError ||
      (err instanceof Error &&
        err.message === "fetch failed" &&
        (causeCode === "ECONNREFUSED" ||
          causeCode === "ENOTFOUND" ||
          causeCode === "ETIMEDOUT" ||
          causeCode === "ECONNRESET"));

    if (isFetchNetworkFailure) {
      console.error("[api/auth/login] upstream unreachable:", authLoginUrl || "(url not built)", err);
      return NextResponse.json(
        {
          message:
            "Backend API unreachable (connection failed). Start Django on port 8000 and verify API_ORIGIN / NEXT_PUBLIC_API_URL in frontend/.env.local match that server.",
        },
        { status: 502 },
      );
    }

    console.error("[api/auth/login]", err);
    return NextResponse.json({ message: "Internal server error." }, { status: 500 });
  }
}

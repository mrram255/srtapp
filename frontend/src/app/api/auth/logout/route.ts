import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { ACCESS_COOKIE, REFRESH_COOKIE } from "@/lib/auth/constants";

function bearerFromRequest(request: Request): string | undefined {
  const raw = request.headers.get("authorization");
  if (!raw?.startsWith("Bearer ")) return undefined;
  const token = raw.slice(7).trim();
  return token.length > 0 ? token : undefined;
}

export async function POST(request: Request) {
  let refreshFromBody: string | undefined;
  try {
    const json = (await request.json()) as { refresh?: unknown };
    refreshFromBody = typeof json.refresh === "string" ? json.refresh : undefined;
  } catch {
    refreshFromBody = undefined;
  }

  const cookieStore = await cookies();
  const access = cookieStore.get(ACCESS_COOKIE)?.value ?? bearerFromRequest(request) ?? "";
  const refresh = cookieStore.get(REFRESH_COOKIE)?.value ?? refreshFromBody ?? "";

  const apiBase =
    process.env.API_ORIGIN ??
    process.env.NEXT_PUBLIC_API_URL ??
    "http://localhost:8000/api/v1";

  if (access && refresh) {
    const logoutUrl = `${apiBase.replace(/\/$/, "")}/auth/logout/`;
    try {
      await fetch(logoutUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${access}`,
        },
        body: JSON.stringify({ refresh_token: refresh }),
      });
    } catch {
      /* still clear cookies locally */
    }
  }

  const res = NextResponse.json({ ok: true });
  res.cookies.delete(ACCESS_COOKIE);
  res.cookies.delete(REFRESH_COOKIE);
  return res;
}

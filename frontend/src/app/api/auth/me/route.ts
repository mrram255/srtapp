import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { ACCESS_COOKIE } from "@/lib/auth/constants";
import { verifyAccessToken } from "@/lib/auth/jwt";
import type { AuthUser } from "@/types";

type DjangoEnvelope<T = unknown> = {
  success?: boolean;
  message?: string;
  data?: T;
};

function normalizeAuthUser(raw: Record<string, unknown>): AuthUser {
  return {
    id: String(raw.id ?? ""),
    email: String(raw.email ?? ""),
    role: String(raw.role ?? ""),
    first_name: String(raw.first_name ?? ""),
    last_name: String(raw.last_name ?? ""),
    college_id: raw.college_id != null ? String(raw.college_id) : raw.college != null ? String(raw.college) : null,
    department_id:
      raw.department_id != null ? String(raw.department_id) : raw.department != null ? String(raw.department) : null,
    is_verified: Boolean(raw.is_verified),
    must_change_password: Boolean(raw.must_change_password),
    profile_photo: String(raw.profile_photo ?? ""),
    signature: String(raw.signature ?? ""),
  };
}

export async function GET() {
  const cookieStore = await cookies();
  const token = cookieStore.get(ACCESS_COOKIE)?.value;
  if (!token) {
    return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
  }

  const session = await verifyAccessToken(token);
  if (!session) {
    return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
  }

  const apiBase =
    process.env.API_ORIGIN ??
    process.env.NEXT_PUBLIC_API_URL ??
    "http://localhost:8000/api/v1";

  const profileUrl = `${apiBase.replace(/\/$/, "")}/auth/me/`;

  const upstream = await fetch(profileUrl, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  let payload: DjangoEnvelope<Record<string, unknown>>;
  try {
    payload = (await upstream.json()) as DjangoEnvelope<Record<string, unknown>>;
  } catch {
    return NextResponse.json({ message: "Unexpected response from auth server." }, { status: 502 });
  }

  const rawUser = payload.data;
  if (!upstream.ok || payload.success === false || !rawUser || typeof rawUser !== "object") {
    const status = upstream.status >= 400 ? upstream.status : 401;
    const message =
      typeof payload.message === "string" && payload.message.length > 0 ? payload.message : "Unauthorized.";
    return NextResponse.json({ message }, { status });
  }

  const user = normalizeAuthUser(rawUser);
  return NextResponse.json({ user });
}

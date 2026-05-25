import { NextResponse } from "next/server";
import { cookies } from "next/headers";

import { ACCESS_COOKIE } from "@/lib/auth/constants";

export async function POST(request: Request) {
  const cookieStore = await cookies();
  const token = cookieStore.get(ACCESS_COOKIE)?.value;
  if (!token) {
    return NextResponse.json({ message: "Not authenticated." }, { status: 401 });
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ message: "Invalid JSON body." }, { status: 400 });
  }

  const apiBase =
    process.env.API_ORIGIN ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

  const upstream = await fetch(`${apiBase.replace(/\/$/, "")}/auth/password/change/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });

  const payload = (await upstream.json()) as { message?: string; success?: boolean };
  if (!upstream.ok) {
    return NextResponse.json(
      { message: payload.message ?? "Password change failed." },
      { status: upstream.status },
    );
  }

  return NextResponse.json({ ok: true, message: payload.message ?? "Password changed." });
}

import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const body = await request.json() as Record<string, unknown>;
    const apiBase = process.env.API_ORIGIN ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
    const upstream = await fetch(`${apiBase.replace(/\/$/, "")}/auth/email/verify/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const payload = await upstream.json() as { success?: boolean; message?: string };
    if (!upstream.ok) {
      return NextResponse.json({ message: payload.message ?? "Verification failed." }, { status: upstream.status });
    }
    return NextResponse.json({ ok: true, message: payload.message });
  } catch {
    return NextResponse.json({ message: "Internal server error." }, { status: 500 });
  }
}

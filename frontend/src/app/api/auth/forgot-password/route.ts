import { NextResponse } from "next/server";

type DjangoEnvelope = { success?: boolean; message?: string };

export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ message: "Invalid JSON body." }, { status: 400 });
  }

  const email =
    typeof body === "object" && body !== null && "email" in body
      ? String((body as { email?: unknown }).email ?? "").trim()
      : "";

  if (!email) {
    return NextResponse.json({ message: "Email is required." }, { status: 400 });
  }

  const apiBase =
    process.env.API_ORIGIN ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

  const upstream = await fetch(`${apiBase.replace(/\/$/, "")}/auth/password/reset/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  let payload: DjangoEnvelope;
  try {
    payload = (await upstream.json()) as DjangoEnvelope;
  } catch {
    return NextResponse.json({ message: "Unexpected response from auth server." }, { status: 502 });
  }

  const message =
    typeof payload.message === "string" && payload.message.length > 0
      ? payload.message
      : "If this email exists, OTP has been sent.";

  return NextResponse.json({ ok: upstream.ok, message }, { status: upstream.ok ? 200 : upstream.status });
}

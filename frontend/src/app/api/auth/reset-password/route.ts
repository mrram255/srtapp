import { NextResponse } from "next/server";

type DjangoEnvelope = { success?: boolean; message?: string; errors?: unknown };

export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ message: "Invalid JSON body." }, { status: 400 });
  }

  const data = body as {
    email?: string;
    otp?: string;
    new_password?: string;
    confirm_password?: string;
  };

  if (!data.email || !data.otp || !data.new_password || !data.confirm_password) {
    return NextResponse.json({ message: "All fields are required." }, { status: 400 });
  }

  if (data.new_password !== data.confirm_password) {
    return NextResponse.json({ message: "Passwords do not match." }, { status: 400 });
  }

  const apiBase =
    process.env.API_ORIGIN ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

  const upstream = await fetch(`${apiBase.replace(/\/$/, "")}/auth/password/reset/confirm/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: data.email,
      otp_code: data.otp,
      new_password: data.new_password,
      confirm_password: data.confirm_password,
    }),
  });

  let payload: DjangoEnvelope;
  try {
    payload = (await upstream.json()) as DjangoEnvelope;
  } catch {
    return NextResponse.json({ message: "Unexpected response from auth server." }, { status: 502 });
  }

  if (!upstream.ok) {
    const message =
      typeof payload.message === "string" && payload.message.length > 0
        ? payload.message
        : "Password reset failed.";
    return NextResponse.json({ message, errors: payload.errors }, { status: upstream.status });
  }

  return NextResponse.json({
    ok: true,
    message: payload.message ?? "Password reset successful. You can sign in now.",
  });
}

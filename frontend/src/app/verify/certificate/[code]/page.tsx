"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Award, CheckCircle, XCircle } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

interface VerifyData {
  valid?: boolean;
  student_name?: string;
  enrollment_number?: string;
  college?: string;
  department?: string;
  certificate?: string;
  certificate_type?: string;
  certificate_number?: string;
  verification_code?: string;
  issued_at?: string;
  message?: string;
  revoked_reason?: string;
}

export default function PublicCertificateVerifyPage() {
  const params = useParams();
  const code = String(params.code ?? "");
  const [data, setData] = useState<VerifyData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!code) return;
    fetch(`${API_BASE}/certificates/verify/${encodeURIComponent(code)}/`)
      .then((r) => r.json())
      .then((body) => setData(body.data ?? body))
      .catch(() => setData({ valid: false, message: "Verification failed." }))
      .finally(() => setLoading(false));
  }, [code]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <p className="text-gray-500">Verifying certificate…</p>
      </div>
    );
  }

  const valid = data?.valid === true;

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-slate-50 to-slate-100 p-6">
      <div className="w-full max-w-lg rounded-2xl border bg-white p-8 shadow-lg">
        <div className="flex items-center gap-3 border-b pb-4">
          <Award className="h-8 w-8 text-indigo-600" />
          <div>
            <h1 className="text-xl font-bold text-gray-900">Certificate Verification</h1>
            <p className="text-sm text-gray-500">SRTAPP official registry</p>
          </div>
        </div>

        <div className="mt-6 flex flex-col items-center text-center">
          {valid ? (
            <CheckCircle className="h-16 w-16 text-green-500" />
          ) : (
            <XCircle className="h-16 w-16 text-red-500" />
          )}
          <p className={`mt-3 text-lg font-semibold ${valid ? "text-green-700" : "text-red-700"}`}>
            {valid ? "Valid certificate" : data?.message ?? "Invalid certificate"}
          </p>
        </div>

        {valid && data ? (
          <dl className="mt-6 space-y-3 text-sm">
            <Row label="Student" value={data.student_name} />
            <Row label="Enrollment" value={data.enrollment_number} />
            <Row label="College" value={data.college} />
            <Row label="Department" value={data.department} />
            <Row label="Certificate" value={data.certificate} />
            <Row label="Certificate No." value={data.certificate_number} />
            <Row label="Verification code" value={data.verification_code} />
            {data.issued_at ? <Row label="Issued" value={String(data.issued_at)} /> : null}
          </dl>
        ) : data?.revoked_reason ? (
          <p className="mt-4 text-sm text-red-600">Reason: {data.revoked_reason}</p>
        ) : null}
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value?: string }) {
  if (!value) return null;
  return (
    <div className="flex justify-between gap-4 border-b border-gray-100 py-2">
      <dt className="text-gray-500">{label}</dt>
      <dd className="font-medium text-gray-900 text-right">{value}</dd>
    </div>
  );
}

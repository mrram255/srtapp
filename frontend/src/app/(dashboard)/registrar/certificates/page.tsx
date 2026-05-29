"use client";

import { useCallback, useEffect, useState } from "react";
import { Award, Check, FileText, X } from "lucide-react";
import api from "@/lib/api/client";

type Tab = "requests" | "issued" | "templates";

interface CertRequest {
  id: string;
  request_number: string;
  student_name: string;
  student_enrollment: string;
  template_name: string;
  status: string;
  purpose: string;
}

interface CertIssue {
  id: string;
  student_name: string;
  student_enrollment: string;
  template_name: string;
  certificate_number: string;
  verification_code: string;
  pdf_url?: string;
  is_revoked?: boolean;
}

interface Template {
  id: string;
  name: string;
  code: string;
  certificate_type: string;
  requires_approval: boolean;
  auto_generate: boolean;
}

interface Stats {
  requests: { pending: number; approved: number; rejected: number; issued: number };
  issued: { total: number; revoked: number };
}

export default function RegistrarCertificatesPage() {
  const [tab, setTab] = useState<Tab>("requests");
  const [requests, setRequests] = useState<CertRequest[]>([]);
  const [issues, setIssues] = useState<CertIssue[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [verifyCode, setVerifyCode] = useState("");
  const [verifyResult, setVerifyResult] = useState<Record<string, unknown> | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const reqParams = statusFilter ? `?status=${statusFilter}&limit=100` : "?limit=100";
      const [reqRes, issRes, tplRes, statsRes] = await Promise.all([
        api.get<{ data?: CertRequest[] }>(`/certificates/requests${reqParams}`),
        api.get<{ data?: CertIssue[] }>("/certificates/issues/?limit=100"),
        api.get<{ data?: Template[] }>("/certificates/templates/?limit=50"),
        api.get<{ data?: Stats }>("/certificates/stats/"),
      ]);
      setRequests(reqRes.data.data ?? []);
      setIssues(issRes.data.data ?? []);
      setTemplates(tplRes.data.data ?? []);
      setStats(statsRes.data.data ?? null);
    } catch {
      setError("Failed to load certificates.");
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    void load();
  }, [load]);

  const approve = async (id: string, autoIssue = false) => {
    await api.post(`/certificates/requests/${id}/approve/`, { remarks: "Approved", auto_issue: autoIssue });
    await load();
  };

  const reject = async (id: string) => {
    await api.post(`/certificates/requests/${id}/reject/`, { remarks: "Rejected" });
    await load();
  };

  const generate = async (id: string) => {
    await api.post(`/certificates/requests/${id}/generate/`);
    await load();
  };

  const revoke = async (id: string) => {
    await api.post(`/certificates/issues/${id}/revoke/`, { reason: "Revoked by registrar" });
    await load();
  };

  const runVerify = async () => {
    if (!verifyCode.trim()) return;
    try {
      const res = await api.get<{ data?: Record<string, unknown> }>(
        `/certificates/verify/${encodeURIComponent(verifyCode.trim())}/`,
      );
      setVerifyResult(res.data.data ?? res.data);
    } catch {
      setVerifyResult({ valid: false, message: "Not found" });
    }
  };

  const pending = requests.filter((r) => r.status === "pending");
  const approved = requests.filter((r) => r.status === "approved");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-primary flex items-center gap-2">
          <Award className="h-6 w-6" /> Certificate Management
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">Pending requests, issued certificates, templates</p>
      </div>

      {stats ? (
        <div className="grid gap-3 sm:grid-cols-4">
          <StatCard label="Pending" value={stats.requests.pending} />
          <StatCard label="Approved" value={stats.requests.approved} />
          <StatCard label="Issued" value={stats.issued.total} />
          <StatCard label="Revoked" value={stats.issued.revoked} />
        </div>
      ) : null}

      {error ? <p className="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</p> : null}

      <div className="flex flex-wrap items-center gap-2">
        {(["requests", "issued", "templates"] as Tab[]).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`rounded-lg px-3 py-2 text-sm font-medium capitalize ${
              tab === t ? "bg-accent text-white" : "bg-muted text-muted-foreground"
            }`}
          >
            {t}
          </button>
        ))}
        {tab === "requests" ? (
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="ml-auto rounded-lg border border-border bg-background px-3 py-2 text-sm"
          >
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="issued">Issued</option>
            <option value="rejected">Rejected</option>
          </select>
        ) : null}
      </div>

      {loading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : tab === "requests" ? (
        <div className="space-y-4">
          {pending.length > 0 ? (
            <RequestSection title="Pending approval">
              {pending.map((r) => (
                <RequestRow key={r.id} request={r}>
                  <button type="button" onClick={() => void approve(r.id, true)} className="btn-green">
                    <Check className="h-3 w-3" /> Approve & issue
                  </button>
                  <button type="button" onClick={() => void approve(r.id)} className="btn-outline">
                    Approve
                  </button>
                  <button type="button" onClick={() => void reject(r.id)} className="btn-outline">
                    <X className="h-3 w-3" /> Reject
                  </button>
                </RequestRow>
              ))}
            </RequestSection>
          ) : null}
          {approved.length > 0 ? (
            <RequestSection title="Ready to generate">
              {approved.map((r) => (
                <RequestRow key={r.id} request={r}>
                  <button type="button" onClick={() => void generate(r.id)} className="btn-accent">
                    Generate PDF
                  </button>
                </RequestRow>
              ))}
            </RequestSection>
          ) : null}
          {pending.length === 0 && approved.length === 0 ? (
            <p className="text-sm text-muted-foreground">No open requests.</p>
          ) : null}
        </div>
      ) : tab === "issued" ? (
        <div className="overflow-hidden rounded-xl border border-border bg-surface">
          <table className="min-w-full text-sm">
            <thead className="bg-muted/50 text-left">
              <tr>
                <th className="px-4 py-3">Student</th>
                <th className="px-4 py-3">Certificate</th>
                <th className="px-4 py-3">Number</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {issues.map((i) => (
                <tr key={i.id} className="border-t border-border">
                  <td className="px-4 py-3">
                    <p className="font-medium">{i.student_name}</p>
                    <p className="text-xs text-muted-foreground">{i.student_enrollment}</p>
                  </td>
                  <td className="px-4 py-3">{i.template_name}</td>
                  <td className="px-4 py-3 font-mono text-xs">{i.certificate_number || i.verification_code}</td>
                  <td className="px-4 py-3 flex gap-2">
                    {i.pdf_url ? (
                      <a href={i.pdf_url} target="_blank" rel="noreferrer" className="text-accent text-xs hover:underline">
                        <FileText className="inline h-4 w-4" /> PDF
                      </a>
                    ) : null}
                    {!i.is_revoked ? (
                      <button type="button" onClick={() => void revoke(i.id)} className="text-xs text-red-600">
                        Revoke
                      </button>
                    ) : (
                      <span className="text-xs text-red-500">Revoked</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {templates.map((t) => (
            <div key={t.id} className="rounded-xl border border-border bg-surface p-4 text-sm">
              <p className="font-semibold">{t.name}</p>
              <p className="text-xs text-muted-foreground">{t.code} · {t.certificate_type}</p>
              <p className="mt-2 text-xs">
                {t.requires_approval ? "Requires approval" : "No approval"} ·{" "}
                {t.auto_generate ? "Auto-issue" : "Manual issue"}
              </p>
            </div>
          ))}
        </div>
      )}

      <section className="rounded-xl border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold">Public verification</h2>
        <div className="mt-2 flex flex-wrap gap-2">
          <input
            value={verifyCode}
            onChange={(e) => setVerifyCode(e.target.value)}
            placeholder="Verification or certificate number"
            className="flex-1 min-w-[200px] rounded-lg border border-border bg-background px-3 py-2 text-sm"
          />
          <button type="button" onClick={() => void runVerify()} className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground">
            Verify
          </button>
        </div>
        {verifyResult ? (
          <pre className="mt-3 overflow-auto rounded-lg bg-muted p-3 text-xs">{JSON.stringify(verifyResult, null, 2)}</pre>
        ) : null}
      </section>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-border bg-surface p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
}

function RequestSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-xl border border-border bg-surface overflow-hidden">
      <h2 className="border-b border-border px-4 py-3 text-sm font-semibold">{title}</h2>
      <ul className="divide-y divide-border">{children}</ul>
    </section>
  );
}

function RequestRow({ request, children }: { request: CertRequest; children: React.ReactNode }) {
  return (
    <li className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 text-sm">
      <div>
        <p className="font-medium">{request.student_name}</p>
        <p className="text-muted-foreground">
          {request.template_name} · {request.request_number}
        </p>
        {request.purpose ? <p className="text-xs text-muted-foreground">{request.purpose}</p> : null}
      </div>
      <div className="flex flex-wrap gap-2">{children}</div>
    </li>
  );
}

"use client";

import { useCallback, useEffect, useState } from "react";
import { Award, Download, Plus } from "lucide-react";
import api from "@/lib/api/client";
import { useAuthStore } from "@/store/auth-store";

interface Template {
  id: string;
  name: string;
  code: string;
  certificate_type: string;
  requires_approval: boolean;
}

interface CertRequest {
  id: string;
  request_number: string;
  template_name: string;
  status: string;
  purpose: string;
  created_at: string;
}

interface CertIssue {
  id: string;
  template_name: string;
  certificate_number: string;
  verification_code: string;
  pdf_url?: string;
  issued_at?: string;
}

export default function StudentCertificatesPage() {
  const { user } = useAuthStore();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [requests, setRequests] = useState<CertRequest[]>([]);
  const [certificates, setCertificates] = useState<CertIssue[]>([]);
  const [templateId, setTemplateId] = useState("");
  const [purpose, setPurpose] = useState("");
  const [studentId, setStudentId] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    if (!user?.id) return;
    setLoading(true);
    setError("");
    try {
      const [tRes, rRes, cRes, meRes] = await Promise.all([
        api.get<{ data?: Template[] }>("/certificates/templates/?limit=50"),
        api.get<{ data?: CertRequest[] }>("/certificates/my-requests/?limit=50"),
        api.get<{ data?: CertIssue[] }>("/certificates/my-certificates/?limit=50"),
        api.get<{ data?: { id: string } }>("/students/me/").catch(() => ({ data: { data: null } })),
      ]);
      setTemplates(tRes.data.data ?? []);
      setRequests(rRes.data.data ?? []);
      setCertificates(cRes.data.data ?? []);
      const me = meRes.data as { data?: { id: string }; id?: string };
      const sid = me?.data?.id ?? (me as { id?: string })?.id;
      if (sid) setStudentId(sid);
    } catch {
      setError("Failed to load certificates.");
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    void load();
  }, [load]);

  const submitRequest = async () => {
    if (!templateId || !studentId) return;
    setSubmitting(true);
    setError("");
    try {
      await api.post("/certificates/request/", {
        student: studentId,
        template: templateId,
        purpose,
      });
      setPurpose("");
      setTemplateId("");
      await load();
    } catch {
      setError("Could not submit request.");
    } finally {
      setSubmitting(false);
    }
  };

  const download = async (id: string) => {
    try {
      const res = await api.get<{ data?: { download_url?: string } }>(`/certificates/download/${id}/`);
      const url = res.data.data?.download_url;
      if (url) window.open(url, "_blank");
    } catch {
      setError("Download failed.");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-primary flex items-center gap-2">
          <Award className="h-6 w-6" /> My Certificates
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">Request, track, and download issued certificates</p>
      </div>

      {error ? <p className="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</p> : null}

      <section className="rounded-xl border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold flex items-center gap-2">
          <Plus className="h-4 w-4" /> New request
        </h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <label className="block text-sm">
            <span className="text-muted-foreground">Certificate type</span>
            <select
              className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2"
              value={templateId}
              onChange={(e) => setTemplateId(e.target.value)}
            >
              <option value="">Select template</option>
              {templates.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name} ({t.certificate_type})
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm sm:col-span-2">
            <span className="text-muted-foreground">Purpose</span>
            <input
              className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2"
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              placeholder="Why do you need this certificate?"
            />
          </label>
        </div>
        <button
          type="button"
          disabled={submitting || !templateId}
          onClick={() => void submitRequest()}
          className="mt-3 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {submitting ? "Submitting…" : "Submit request"}
        </button>
      </section>

      {loading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : (
        <>
          <section className="rounded-xl border border-border bg-surface overflow-hidden">
            <h2 className="border-b border-border px-4 py-3 text-sm font-semibold">My requests</h2>
            <ul className="divide-y divide-border text-sm">
              {requests.map((r) => (
                <li key={r.id} className="flex justify-between gap-3 px-4 py-3">
                  <div>
                    <p className="font-medium">{r.template_name}</p>
                    <p className="text-xs text-muted-foreground">{r.request_number}</p>
                    {r.purpose ? <p className="text-xs text-muted-foreground">{r.purpose}</p> : null}
                  </div>
                  <span className="rounded-full bg-muted px-2 py-0.5 text-xs capitalize">{r.status}</span>
                </li>
              ))}
              {requests.length === 0 ? (
                <li className="px-4 py-6 text-center text-muted-foreground">No requests yet.</li>
              ) : null}
            </ul>
          </section>

          <section className="rounded-xl border border-border bg-surface overflow-hidden">
            <h2 className="border-b border-border px-4 py-3 text-sm font-semibold">Issued certificates</h2>
            <ul className="divide-y divide-border text-sm">
              {certificates.map((c) => (
                <li key={c.id} className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
                  <div>
                    <p className="font-medium">{c.template_name}</p>
                    <p className="font-mono text-xs text-muted-foreground">{c.certificate_number}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => void download(c.id)}
                    className="inline-flex items-center gap-1 rounded-lg border px-2 py-1 text-xs hover:bg-muted"
                  >
                    <Download className="h-3 w-3" /> Download
                  </button>
                </li>
              ))}
              {certificates.length === 0 ? (
                <li className="px-4 py-6 text-center text-muted-foreground">No issued certificates.</li>
              ) : null}
            </ul>
          </section>
        </>
      )}
    </div>
  );
}

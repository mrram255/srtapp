"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api/client";

interface AuditRow {
  id: string;
  module: string;
  action: string;
  object_repr: string;
  user_email?: string;
  created_at: string;
  response_status: number | null;
}

export default function AuditLogPage() {
  const [rows, setRows] = useState<AuditRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/audit/logs/")
      .then((r) => setRows(r.data.data ?? []))
      .catch(() => setRows([]))
      .finally(() => setLoading(false));
  }, []);

  const handleExport = () => {
    window.open("/django-api/audit/export/", "_blank");
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Audit log</h1>
        <button
          type="button"
          onClick={handleExport}
          className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white"
        >
          Export CSV
        </button>
      </div>
      {loading ? (
        <p className="text-muted-foreground">Loading…</p>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-border">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-4 py-2 text-left">Time</th>
                <th className="px-4 py-2 text-left">Module</th>
                <th className="px-4 py-2 text-left">Action</th>
                <th className="px-4 py-2 text-left">Object</th>
                <th className="px-4 py-2 text-left">Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className="border-t border-border">
                  <td className="px-4 py-2">{new Date(row.created_at).toLocaleString()}</td>
                  <td className="px-4 py-2">{row.module}</td>
                  <td className="px-4 py-2">{row.action}</td>
                  <td className="px-4 py-2">{row.object_repr}</td>
                  <td className="px-4 py-2">{row.response_status ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

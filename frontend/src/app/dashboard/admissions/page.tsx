"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import api from "@/lib/api/client";

export default function AdmissionsPage() {
  const [apps, setApps] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    api.get("/admissions/").then((r) => setApps(r.data.data ?? [])).catch(() => {});
  }, []);

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Admissions</h1>
        <div className="flex gap-2">
          <Link href="/dashboard/admissions/kanban" className="rounded-lg border border-border px-4 py-2 text-sm">
            CRM Kanban
          </Link>
          <Link href="/apply" className="rounded-lg bg-accent px-4 py-2 text-sm text-white">
            Public apply
          </Link>
        </div>
      </div>
      <ul className="divide-y rounded-xl border border-border">
        {apps.map((a) => (
          <li key={String(a.id)} className="flex justify-between px-4 py-3 text-sm">
            <span>
              {String(a.application_number)} — {String(a.first_name)} {String(a.last_name)}
            </span>
            <span className="rounded-full bg-muted px-2 py-0.5 text-xs">{String(a.status)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

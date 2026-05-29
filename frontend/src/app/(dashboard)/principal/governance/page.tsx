"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api/client";

export default function PrincipalGovernancePage() {
  const [approvals, setApprovals] = useState<Record<string, unknown>[]>([]);
  const [meetings, setMeetings] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    Promise.all([
      api.get("/governance/approvals/").then((r) => setApprovals(r.data.data ?? [])),
      api.get("/meetings/").then((r) => setMeetings(r.data.data ?? [])),
    ]).catch(() => {});
  }, []);

  return (
    <div className="space-y-8 p-6">
      <h1 className="text-2xl font-bold">Governance</h1>
      <section>
        <h2 className="mb-3 font-semibold">Pending approvals</h2>
        <ul className="divide-y rounded-xl border border-border">
          {approvals.filter((a) => a.status === "pending").map((a) => (
            <li key={String(a.id)} className="px-4 py-3 text-sm">
              <p className="font-medium">{String(a.title)}</p>
              <p className="text-muted-foreground">{String(a.request_type)}</p>
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h2 className="mb-3 font-semibold">Meetings</h2>
        <ul className="divide-y rounded-xl border border-border">
          {meetings.map((m) => (
            <li key={String(m.id)} className="flex justify-between px-4 py-3 text-sm">
              <span>{String(m.title)}</span>
              <span className="text-muted-foreground">{String(m.status)}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

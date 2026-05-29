"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api/client";

const COLUMNS = [
  "DRAFT",
  "SUBMITTED",
  "UNDER_REVIEW",
  "SHORTLISTED",
  "ACCEPTED",
  "REJECTED",
  "ENROLLED",
] as const;

type KanbanData = Record<string, Array<Record<string, unknown>>>;

export default function AdmissionsKanbanPage() {
  const [board, setBoard] = useState<KanbanData>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/admissions/kanban/")
      .then((r) => setBoard(r.data.data ?? {}))
      .catch(() => setBoard({}))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="p-6 text-muted-foreground">Loading kanban…</p>;
  }

  return (
    <div className="space-y-4 p-6">
      <h1 className="text-2xl font-bold">Admissions CRM</h1>
      <div className="flex gap-4 overflow-x-auto pb-4">
        {COLUMNS.map((col) => (
          <div key={col} className="min-w-[240px] shrink-0 rounded-xl border border-border bg-muted/30">
            <div className="border-b border-border px-3 py-2 text-sm font-semibold">
              {col.replace(/_/g, " ")}
              <span className="ml-2 text-muted-foreground">({(board[col] ?? []).length})</span>
            </div>
            <div className="space-y-2 p-2">
              {(board[col] ?? []).map((card) => (
                <div key={String(card.id)} className="rounded-lg border border-border bg-surface p-3 text-sm shadow-sm">
                  <p className="font-medium">
                    {String(card.first_name)} {String(card.last_name)}
                  </p>
                  <p className="text-xs text-muted-foreground">{String(card.application_number)}</p>
                  <p className="mt-1 text-xs">{String(card.department_name ?? "")}</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

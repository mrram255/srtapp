"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api/client";
import { formatCurrency } from "@/lib/utils";

export default function PayrollPage() {
  const [runs, setRuns] = useState<Record<string, unknown>[]>([]);
  const [payslips, setPayslips] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    Promise.all([
      api.get("/finance/payroll/runs/").then((r) => setRuns(r.data.data ?? [])),
      api.get("/finance/payroll/payslips/").then((r) => setPayslips(r.data.data ?? [])),
    ]).catch(() => {});
  }, []);

  const processPayroll = async () => {
    const now = new Date();
    await api.post("/finance/payroll/runs/", { month: now.getMonth() + 1, year: now.getFullYear() });
    const r = await api.get("/finance/payroll/runs/");
    setRuns(r.data.data ?? []);
    const p = await api.get("/finance/payroll/payslips/");
    setPayslips(p.data.data ?? []);
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Payroll</h1>
        <button type="button" onClick={() => void processPayroll()} className="rounded-lg bg-accent px-4 py-2 text-sm text-white">
          Process this month
        </button>
      </div>
      <section>
        <h2 className="mb-2 font-semibold">Payroll runs</h2>
        <ul className="divide-y rounded-xl border border-border">
          {runs.map((run) => (
            <li key={String(run.id)} className="flex justify-between px-4 py-3 text-sm">
              <span>
                {String(run.month)}/{String(run.year)} — {String(run.status)}
              </span>
              <span>{formatCurrency(Number(run.total_net ?? 0))}</span>
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h2 className="mb-2 font-semibold">Payslips</h2>
        <ul className="divide-y rounded-xl border border-border">
          {payslips.map((p) => (
            <li key={String(p.id)} className="flex justify-between px-4 py-3 text-sm">
              <span>Staff {String(p.staff)}</span>
              <span>{formatCurrency(Number(p.net_salary ?? 0))}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

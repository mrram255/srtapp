"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import api from "@/lib/api/client";
import { formatCurrency } from "@/lib/utils";

export default function FinancePage() {
  const [payments, setPayments] = useState<Record<string, unknown>[]>([]);
  const [defaulters, setDefaulters] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    Promise.all([
      api.get("/finance/payments/").then((r) => setPayments(r.data.data ?? [])),
      api.get("/finance/defaulters/").then((r) => setDefaulters(r.data.data ?? [])),
    ]).catch(() => {});
  }, []);

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Finance</h1>
        <Link href="/dashboard/finance/payroll" className="text-sm text-accent hover:underline">
          Payroll →
        </Link>
      </div>
      <section>
        <h2 className="mb-2 font-semibold">Defaulters ({defaulters.length})</h2>
        {defaulters.length === 0 ? (
          <p className="text-sm text-muted-foreground">No defaulters.</p>
        ) : (
          <ul className="divide-y rounded-xl border border-border">
            {defaulters.map((d) => (
              <li key={String(d.id)} className="flex justify-between px-4 py-3 text-sm">
                <span>{String(d.student_enrollment ?? d.student)}</span>
                <span className="font-medium text-red-600">{formatCurrency(Number(d.balance ?? 0))}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
      <section>
        <h2 className="mb-2 font-semibold">Recent payments</h2>
        <ul className="divide-y rounded-xl border border-border">
          {payments.slice(0, 20).map((p) => (
            <li key={String(p.id)} className="flex justify-between px-4 py-3 text-sm">
              <span>{String(p.student_enrollment)} — {String(p.status)}</span>
              <span>{formatCurrency(Number(p.amount_paid ?? 0))}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

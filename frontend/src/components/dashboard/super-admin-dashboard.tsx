"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import api from "@/lib/api/client";
import { formatCurrency } from "@/lib/utils";

type DashboardPayload = {
  kpis: Record<string, number>;
  naac_radar: { criterion: string; score: number }[];
  heatmap: { department: string; students: number; attendance: number; results: number }[];
  alerts: { id: string; title: string; severity: string; message: string }[];
  monthly_trends: { month: string; fees_collected: number; admissions: number; enrollments: number }[];
  fee_by_status: Record<string, number>;
};

const PIE_COLORS = ["#2563eb", "#16a34a", "#f59e0b", "#ef4444", "#8b5cf6"];

export function SuperAdminDashboard() {
  const [data, setData] = useState<DashboardPayload | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/dashboard/super-admin/")
      .then((r) => setData(r.data.data as DashboardPayload))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-accent" />
      </div>
    );
  }

  if (!data) {
    return <p className="text-muted-foreground">Unable to load dashboard data.</p>;
  }

  const feePie = Object.entries(data.fee_by_status || {}).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold text-primary">Super Admin Dashboard</h1>
          <p className="text-sm text-muted-foreground">Institution-wide KPIs and trends</p>
        </div>
        <div className="flex gap-2">
          <Link href="/super-admin/audit-log" className="rounded-lg border border-border px-3 py-2 text-sm hover:bg-muted">
            Audit log
          </Link>
          <Link href="/super-admin/settings" className="rounded-lg border border-border px-3 py-2 text-sm hover:bg-muted">
            Settings
          </Link>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Students", value: data.kpis.total_students },
          { label: "Teachers", value: data.kpis.total_teachers },
          { label: "Present today", value: data.kpis.present_today },
          { label: "Fee (month)", value: formatCurrency(data.kpis.fee_collected_month || 0) },
        ].map((k) => (
          <div key={k.label} className="rounded-xl border border-border bg-surface p-4 shadow-card">
            <p className="text-sm text-muted-foreground">{k.label}</p>
            <p className="mt-1 text-2xl font-bold">{k.value}</p>
          </div>
        ))}
      </div>

      {data.alerts.length > 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 dark:border-amber-900 dark:bg-amber-950/30">
          <h3 className="font-semibold text-amber-900 dark:text-amber-200">Alerts</h3>
          <ul className="mt-2 space-y-1 text-sm">
            {data.alerts.map((a) => (
              <li key={a.id}>
                <strong>{a.title}:</strong> {a.message}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-border bg-surface p-4 shadow-card">
          <h3 className="mb-4 font-semibold">12-month fee & admissions</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={data.monthly_trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="fees_collected" name="Fees" stroke="#2563eb" />
              <Line type="monotone" dataKey="admissions" name="Applications" stroke="#16a34a" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-xl border border-border bg-surface p-4 shadow-card">
          <h3 className="mb-4 font-semibold">NAAC criteria (radar)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <RadarChart data={data.naac_radar}>
              <PolarGrid />
              <PolarAngleAxis dataKey="criterion" tick={{ fontSize: 10 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} />
              <Radar dataKey="score" stroke="#2563eb" fill="#2563eb" fillOpacity={0.4} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-xl border border-border bg-surface p-4 shadow-card">
          <h3 className="mb-4 font-semibold">Department heatmap</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.heatmap}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="department" tick={{ fontSize: 10 }} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="students" fill="#2563eb" />
              <Bar dataKey="attendance" fill="#16a34a" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-xl border border-border bg-surface p-4 shadow-card">
          <h3 className="mb-4 font-semibold">Fee status (donut)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={feePie} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={100} label>
                {feePie.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

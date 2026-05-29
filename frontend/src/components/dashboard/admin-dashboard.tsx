"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity, BookOpen, CalendarCheck, DollarSign, FileText, GraduationCap, Users,
} from "lucide-react";

import { formatCurrency } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";
import api from "@/lib/api/client";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: ReactNode;
  color: string;
}

function StatCard({ title, value, icon, color }: StatCardProps) {
  return (
    <div className="animate-fade-in rounded-xl border border-border bg-surface p-6 shadow-card">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <h3 className="mt-2 text-2xl font-bold font-numeric text-foreground">{value}</h3>
        </div>
        <div className={`rounded-lg p-3 ${color}`}>{icon}</div>
      </div>
    </div>
  );
}

type DashboardStats = Record<string, number | string | undefined>;

const titles: Record<string, string> = {
  admin: "Admin Dashboard",
  "super-admin": "Super Admin Dashboard",
  principal: "Principal Dashboard",
  registrar: "Registrar Dashboard",
  accounts: "Accounts Dashboard",
  admissions: "Admissions Dashboard",
  hod: "HOD Dashboard",
  accountant: "Accountant Dashboard",
  librarian: "Librarian Dashboard",
  security: "Security Dashboard",
  parent: "Parent Dashboard",
};

export function AdminDashboard({
  segment,
  titleOverride,
}: {
  segment: string;
  titleOverride?: string;
}) {
  const { user } = useAuthStore();
  const heading = titleOverride ?? titles[segment] ?? `${segment.replace(/-/g, " ")} Dashboard`;
  const [stats, setStats] = useState<DashboardStats>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.id) return;
    api
      .get("/analytics/dashboard/")
      .then((r) => setStats((r.data.data ?? {}) as DashboardStats))
      .catch(() => setStats({}))
      .finally(() => setLoading(false));
  }, [user?.id]);

  const cards: StatCardProps[] = [];
  if (stats.total_students != null) {
    cards.push({ title: "Total students", value: stats.total_students, icon: <GraduationCap className="h-6 w-6 text-white" />, color: "bg-accent" });
  }
  if (stats.total_teachers != null) {
    cards.push({ title: "Total teachers", value: stats.total_teachers, icon: <Users className="h-6 w-6 text-white" />, color: "bg-primary" });
  }
  if (stats.present_today != null) {
    cards.push({ title: "Present today", value: stats.present_today, icon: <CalendarCheck className="h-6 w-6 text-white" />, color: "bg-success" });
  }
  if (stats.fee_collected_month != null) {
    cards.push({ title: "Fee collected (month)", value: formatCurrency(Number(stats.fee_collected_month)), icon: <DollarSign className="h-6 w-6 text-white" />, color: "bg-gold" });
  }
  if (stats.dept_students != null) {
    cards.push({ title: "Dept students", value: stats.dept_students, icon: <GraduationCap className="h-6 w-6 text-white" />, color: "bg-accent" });
  }
  if (stats.dept_teachers != null) {
    cards.push({ title: "Dept teachers", value: stats.dept_teachers, icon: <Users className="h-6 w-6 text-white" />, color: "bg-primary" });
  }
  if (stats.pending_assignments != null) {
    cards.push({ title: "Published assignments", value: stats.pending_assignments, icon: <FileText className="h-6 w-6 text-white" />, color: "bg-warning" });
  }
  if (stats.collected_this_month != null) {
    cards.push({ title: "Collected this month", value: formatCurrency(Number(stats.collected_this_month)), icon: <DollarSign className="h-6 w-6 text-white" />, color: "bg-success" });
  }
  if (stats.pending_payments != null) {
    cards.push({ title: "Pending payments", value: stats.pending_payments, icon: <Activity className="h-6 w-6 text-white" />, color: "bg-warning" });
  }
  if (stats.books_borrowed != null) {
    cards.push({ title: "Books borrowed", value: stats.books_borrowed, icon: <BookOpen className="h-6 w-6 text-white" />, color: "bg-accent" });
  }
  if (stats.overdue_books != null) {
    cards.push({ title: "Overdue books", value: stats.overdue_books, icon: <Activity className="h-6 w-6 text-white" />, color: "bg-warning" });
  }
  if (stats.attendance_avg != null) {
    cards.push({ title: "Attendance avg", value: `${stats.attendance_avg}%`, icon: <CalendarCheck className="h-6 w-6 text-white" />, color: "bg-success" });
  }
  if (stats.results_count != null) {
    cards.push({ title: "Exam results", value: stats.results_count, icon: <FileText className="h-6 w-6 text-white" />, color: "bg-info" });
  }

  const quickLinks = [
    { label: "Attendance", href: "/dashboard/attendance" },
    { label: "Assignments", href: "/dashboard/assignments" },
    { label: "Exams", href: "/dashboard/exams" },
    { label: "Analytics", href: "/dashboard/analytics" },
    { label: "Forum", href: "/dashboard/forum" },
    { label: "Notifications", href: "/dashboard/notifications" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold capitalize text-primary">{heading}</h1>
        <p className="mt-1 text-muted-foreground">
          Welcome back, {user?.first_name}! Here&apos;s what&apos;s happening today.
        </p>
      </div>

      {loading ? (
        <div className="flex min-h-[30vh] items-center justify-center">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-accent" />
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {cards.length === 0 ? (
              <p className="text-sm text-muted-foreground col-span-full">No dashboard metrics available for this role yet.</p>
            ) : (
              cards.map((c) => <StatCard key={c.title} {...c} />)
            )}
          </div>

          <div className="rounded-xl border border-border bg-surface p-6 shadow-card">
            <h3 className="text-lg font-semibold text-foreground">Quick actions</h3>
            <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
              {quickLinks.map((a) => (
                <Link
                  key={a.label}
                  href={a.href}
                  className="rounded-lg bg-accent/10 px-4 py-3 text-center text-sm font-medium text-accent hover:bg-accent/20"
                >
                  {a.label}
                </Link>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

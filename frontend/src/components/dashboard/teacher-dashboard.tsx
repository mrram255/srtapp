"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { CalendarCheck, CheckCircle, Clock, FileText, Users } from "lucide-react";

import { useAuthStore } from "@/store/auth-store";
import api from "@/lib/api/client";
import { timetableApi, type TimetableEntry } from "@/lib/api/timetable";

interface TeacherStats {
  my_assignments?: number;
  pending_grading?: number;
  classes_today?: number;
}

export function TeacherDashboard() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<TeacherStats>({});
  const [schedule, setSchedule] = useState<TimetableEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.id) return;
    const load = async () => {
      try {
        const [dashRes, todayRes] = await Promise.all([
          api.get("/analytics/dashboard/"),
          timetableApi.today(),
        ]);
        setStats((dashRes.data.data ?? {}) as TeacherStats);
        const items = todayRes.data?.items ?? todayRes.data ?? [];
        setSchedule(Array.isArray(items) ? items : []);
      } catch {
        setStats({});
        setSchedule([]);
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [user?.id]);

  if (loading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-accent" />
      </div>
    );
  }

  const cards = [
    { label: "My assignments", value: stats.my_assignments ?? 0, icon: FileText, color: "bg-success" },
    { label: "Classes today", value: stats.classes_today ?? schedule.length, icon: Clock, color: "bg-primary" },
    { label: "Pending grading", value: stats.pending_grading ?? 0, icon: CalendarCheck, color: "bg-warning" },
    { label: "Today's periods", value: schedule.length, icon: Users, color: "bg-accent" },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="font-display text-2xl font-bold text-primary">Teacher dashboard</h1>
        <p className="mt-1 text-muted-foreground">
          Welcome back, {user?.first_name}! Manage your classes and students.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((stat) => (
          <div key={stat.label} className="rounded-xl border border-border bg-surface p-6 shadow-card">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{stat.label}</p>
                <p className="mt-2 text-2xl font-bold font-numeric text-foreground">{stat.value}</p>
              </div>
              <div className={`rounded-lg p-3 ${stat.color}`}>
                <stat.icon className="h-5 w-5 text-white" aria-hidden />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-border bg-surface p-6 shadow-card">
          <h3 className="text-lg font-semibold text-foreground">Today&apos;s classes</h3>
          <div className="mt-4 space-y-3">
            {schedule.length === 0 ? (
              <p className="text-sm text-muted-foreground">No classes scheduled today.</p>
            ) : (
              schedule.map((cls) => (
                <div key={cls.id} className="flex items-center gap-4 rounded-lg border border-border p-4">
                  <div className="w-20 text-sm font-medium text-muted-foreground">
                    {cls.start_time?.slice(0, 5)}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-foreground">{cls.subject_name}</p>
                    <p className="text-xs text-muted-foreground">
                      {cls.section} • {cls.room_number || "—"}
                    </p>
                  </div>
                  <CheckCircle className="h-5 w-5 text-success" aria-hidden />
                </div>
              ))
            )}
          </div>
        </div>

        <div className="rounded-xl border border-border bg-surface p-6 shadow-card">
          <h3 className="text-lg font-semibold text-foreground">Quick actions</h3>
          <div className="mt-4 grid grid-cols-2 gap-3">
            {[
              { label: "Mark attendance", href: "/dashboard/attendance" },
              { label: "Assignments", href: "/dashboard/assignments" },
              { label: "Study materials", href: "/dashboard/study-materials" },
              { label: "Exams", href: "/dashboard/exams" },
            ].map((action) => (
              <Link
                key={action.label}
                href={action.href}
                className="rounded-lg bg-accent/10 px-4 py-3 text-center text-sm font-medium text-accent transition-colors hover:bg-accent/20"
              >
                {action.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

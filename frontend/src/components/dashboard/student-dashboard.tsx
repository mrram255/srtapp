"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Bell, BookOpen, CalendarCheck, FileText } from "lucide-react";

import { useAuthStore } from "@/store/auth-store";
import { studentsApi } from "@/lib/api/students";
import { timetableApi, type TimetableEntry } from "@/lib/api/timetable";
import api from "@/lib/api/client";

interface QuickStatProps {
  label: string;
  value: string;
  icon: ReactNode;
  color: string;
  href: string;
}

function QuickStat({ label, value, icon, color, href }: QuickStatProps) {
  return (
    <Link
      href={href}
      className="flex items-center gap-4 rounded-xl border border-border bg-surface p-4 shadow-card transition-all hover:shadow-elevated"
    >
      <div className={`rounded-lg p-3 ${color}`}>{icon}</div>
      <div>
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className="text-lg font-bold text-foreground">{value}</p>
      </div>
    </Link>
  );
}

interface DashboardData {
  attendance_percentage?: number;
  pending_assignments?: number;
  upcoming_exams?: number;
  fee_status?: string;
  recent_notifications?: { title: string; created_at?: string }[];
}

export function StudentDashboard() {
  const { user } = useAuthStore();
  const [data, setData] = useState<DashboardData | null>(null);
  const [schedule, setSchedule] = useState<TimetableEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.id) return;
    const load = async () => {
      try {
        setLoading(true);
        const [dashRes, todayRes] = await Promise.all([
          user.role === "STUDENT"
            ? studentsApi.dashboard()
            : api.get("/analytics/dashboard/").then((r) => r.data),
          timetableApi.today().catch(() => ({ data: [] })),
        ]);
        setData((dashRes.data ?? dashRes) as DashboardData);
        const items = todayRes.data?.items ?? todayRes.data ?? [];
        setSchedule(Array.isArray(items) ? items : []);
      } catch {
        setData({});
        setSchedule([]);
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [user?.id, user?.role]);

  if (loading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-accent" />
      </div>
    );
  }

  const attendance = data?.attendance_percentage ?? 0;
  const pending = data?.pending_assignments ?? 0;
  const exams = data?.upcoming_exams ?? 0;
  const notifications = data?.recent_notifications ?? [];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="rounded-xl bg-gradient-to-r from-primary to-secondary p-6 text-white shadow-elevated">
        <h1 className="font-display text-2xl font-bold">Welcome back, {user?.first_name}!</h1>
        <p className="mt-2 text-white/80">Here&apos;s your academic overview for today.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <QuickStat
          label="Attendance"
          value={`${attendance}%`}
          icon={<CalendarCheck className="h-5 w-5 text-white" />}
          color="bg-success"
          href="/dashboard/attendance"
        />
        <QuickStat
          label="Pending assignments"
          value={String(pending)}
          icon={<FileText className="h-5 w-5 text-white" />}
          color="bg-accent"
          href="/dashboard/assignments"
        />
        <QuickStat
          label="Upcoming exams"
          value={String(exams)}
          icon={<BookOpen className="h-5 w-5 text-white" />}
          color="bg-warning"
          href="/dashboard/exams"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-xl border border-border bg-surface p-6 shadow-card lg:col-span-2">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-foreground">Today&apos;s schedule</h3>
            <Link href="/dashboard/timetable" className="text-sm text-accent hover:underline">
              Full timetable
            </Link>
          </div>
          <div className="mt-4 space-y-3">
            {schedule.length === 0 ? (
              <p className="text-sm text-muted-foreground">No classes scheduled for today.</p>
            ) : (
              schedule.map((item) => (
                <div key={item.id} className="flex items-center gap-4 rounded-lg border border-border bg-background p-4">
                  <div className="w-28 text-sm font-medium text-muted-foreground">
                    {item.start_time?.slice(0, 5)} – {item.end_time?.slice(0, 5)}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-foreground">{item.subject_name}</p>
                    <p className="text-xs text-muted-foreground">{item.room_number || "—"}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-xl border border-border bg-surface p-6 shadow-card">
            <h3 className="text-lg font-semibold text-foreground">Fee status</h3>
            <div className="mt-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Semester fee</span>
                <span className="text-sm font-medium text-success">{data?.fee_status ?? "—"}</span>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-surface p-6 shadow-card">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-foreground">Notifications</h3>
              <Bell className="h-4 w-4 text-muted-foreground" aria-hidden />
            </div>
            <div className="mt-4 space-y-3">
              {notifications.length === 0 ? (
                <p className="text-sm text-muted-foreground">No recent notifications.</p>
              ) : (
                notifications.slice(0, 5).map((notif, i) => (
                  <div key={i} className="flex items-start gap-3 rounded-lg p-2 hover:bg-muted/50">
                    <div className="mt-1 h-2 w-2 shrink-0 rounded-full bg-accent" />
                    <div>
                      <p className="text-sm font-medium text-foreground">{notif.title}</p>
                      {notif.created_at ? (
                        <p className="text-xs text-muted-foreground">
                          {new Date(notif.created_at).toLocaleString("en-IN")}
                        </p>
                      ) : null}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

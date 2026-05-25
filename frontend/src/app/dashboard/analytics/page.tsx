"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth-store";
import api from "@/lib/api/client";
import { TrendingUp, TrendingDown, BookOpen, CalendarCheck, FileText, Award } from "lucide-react";

interface DashboardStats {
  total_students?: number;
  total_teachers?: number;
  present_today?: number;
  fee_collected_month?: number;
  dept_students?: number;
  dept_teachers?: number;
  pending_assignments?: number;
  my_assignments?: number;
  pending_grading?: number;
  attendance_avg?: number;
  results_count?: number;
  books_borrowed?: number;
  collected_this_month?: number;
  pending_payments?: number;
}

interface SubjectAverage {
  subject: string;
  avg_percentage: number;
  exam_count?: number;
  is_weak?: boolean;
}

interface StudentPerformance {
  overall_avg_percentage: number;
  exam_trend: { exam_name: string; percentage: number; date?: string; exam_date?: string }[];
  subject_averages: SubjectAverage[];
  weak_subjects: SubjectAverage[];
  attendance: { avg_percentage: number; subjects_below_75: number };
  assignments: { total: number; submitted: number; graded: number; avg_marks: number };
}

export default function AnalyticsPage() {
  const user = useAuthStore((s) => s.user);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [performance, setPerformance] = useState<StudentPerformance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const isStudent = user?.role === "STUDENT";

  useEffect(() => {
    if (!user?.id) return;
    const fetch = async () => {
      try {
        setLoading(true);
        const statsRes = await api.get("/analytics/dashboard/").then((r) => r.data);
        setStats(statsRes.data);
        if (isStudent) {
          const perfRes = await api.get("/analytics/student/").then((r) => r.data);
          setPerformance(perfRes.data);
        }
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Failed to load analytics.");
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [user?.id, isStudent]);

  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600" />
    </div>
  );

  if (error) return (
    <div className="m-6 p-5 bg-red-50 border border-red-200 rounded-xl text-red-700">⚠️ {error}</div>
  );

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Performance Analytics</h1>
        <p className="text-sm text-gray-500 mt-0.5">Track your academic performance</p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {isStudent ? (
            <>
              <StatCard title="Attendance" value={`${performance?.attendance.avg_percentage ?? 0}%`} icon={<CalendarCheck className="h-5 w-5" />} color="bg-green-500" />
              <StatCard title="Assignments" value={performance?.assignments.total ?? 0} icon={<FileText className="h-5 w-5" />} color="bg-blue-500" />
              <StatCard title="Submitted" value={performance?.assignments.submitted ?? 0} icon={<TrendingUp className="h-5 w-5" />} color="bg-purple-500" />
              <StatCard title="Avg Score" value={`${performance?.overall_avg_percentage ?? 0}%`} icon={<Award className="h-5 w-5" />} color="bg-accent" />
            </>
          ) : (
            <>
              {stats.total_students !== undefined && <StatCard title="Total Students" value={stats.total_students} icon={<BookOpen className="h-5 w-5" />} color="bg-accent" />}
              {stats.total_teachers !== undefined && <StatCard title="Total Teachers" value={stats.total_teachers} icon={<Award className="h-5 w-5" />} color="bg-blue-500" />}
              {stats.present_today !== undefined && <StatCard title="Present Today" value={stats.present_today} icon={<CalendarCheck className="h-5 w-5" />} color="bg-green-500" />}
              {stats.dept_students !== undefined && <StatCard title="Dept Students" value={stats.dept_students} icon={<BookOpen className="h-5 w-5" />} color="bg-accent" />}
              {stats.dept_teachers !== undefined && <StatCard title="Dept Teachers" value={stats.dept_teachers} icon={<Award className="h-5 w-5" />} color="bg-blue-500" />}
              {stats.pending_assignments !== undefined && <StatCard title="Assignments" value={stats.pending_assignments} icon={<FileText className="h-5 w-5" />} color="bg-warning" />}
              {stats.my_assignments !== undefined && <StatCard title="My Assignments" value={stats.my_assignments} icon={<FileText className="h-5 w-5" />} color="bg-blue-500" />}
              {stats.pending_grading !== undefined && <StatCard title="Pending Grading" value={stats.pending_grading} icon={<TrendingDown className="h-5 w-5" />} color="bg-warning" />}
            </>
          )}
        </div>
      )}

      {/* Student Performance Details */}
      {isStudent && performance && (
        <>
          {/* Exam Trend */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Exam Performance Trend</h2>
            {performance.exam_trend.length === 0 ? (
              <EmptyState title="No exam results yet" />
            ) : (
              <div className="space-y-3">
                {performance.exam_trend.map((exam, i) => (
                  <div key={i} className="flex items-center gap-4">
                    <div className="flex-1">
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium text-gray-700">{exam.exam_name}</span>
                        <span className="text-sm font-bold text-gray-900">{exam.percentage}%</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${exam.percentage >= 75 ? "bg-green-500" : exam.percentage >= 50 ? "bg-yellow-500" : "bg-red-500"}`}
                          style={{ width: `${exam.percentage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Subject Averages */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Subject Averages</h2>
              {performance.subject_averages.length === 0 ? (
                <EmptyState title="No subject data yet" />
              ) : (
                <div className="space-y-3">
                  {performance.subject_averages.map((s, i) => (
                    <div key={i} className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">{s.subject}</span>
                      <span className={`text-sm font-bold ${s.avg_percentage >= 75 ? "text-green-600" : s.avg_percentage >= 50 ? "text-yellow-600" : "text-red-600"}`}>
                        {s.avg_percentage.toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Weak Subjects</h2>
              {performance.weak_subjects.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-4xl mb-2">🎉</p>
                  <p className="text-sm text-gray-500">No weak subjects!</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {performance.weak_subjects.map((s, i) => (
                    <div key={i} className="flex items-center gap-2 p-3 bg-red-50 rounded-lg">
                      <span className="text-red-500">⚠️</span>
                      <span className="text-sm text-red-700 font-medium">
                        {s.subject} ({s.avg_percentage}%)
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Attendance & Assignments Summary */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Attendance Summary</h2>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm text-gray-600">Overall Attendance</span>
                    <span className="text-sm font-bold">{performance.attendance.avg_percentage}%</span>
                  </div>
                  <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${performance.attendance.avg_percentage >= 75 ? "bg-green-500" : "bg-red-500"}`}
                      style={{ width: `${performance.attendance.avg_percentage}%` }} />
                  </div>
                  {performance.attendance.avg_percentage < 75 && (
                    <p className="text-xs text-red-500 mt-1">⚠️ Below 75% minimum requirement</p>
                  )}
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-600">Subjects below 75%</span>
                  <span className="text-sm font-bold text-red-600">{performance.attendance.subjects_below_75}</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Assignment Summary</h2>
              <div className="space-y-3">
                {[
                  { label: "Total Assignments", value: performance.assignments.total, color: "text-gray-900" },
                  { label: "Submitted", value: performance.assignments.submitted, color: "text-blue-600" },
                  { label: "Graded", value: performance.assignments.graded, color: "text-green-600" },
                  { label: "Avg Marks", value: `${performance.assignments.avg_marks.toFixed(1)}`, color: "text-purple-600" },
                ].map((item) => (
                  <div key={item.label} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm text-gray-600">{item.label}</span>
                    <span className={`text-sm font-bold ${item.color}`}>{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function StatCard({ title, value, icon, color }: { title: string; value: string | number; icon: React.ReactNode; color: string }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{title}</p>
        <div className={`p-2 rounded-lg ${color}`}>{icon && <span className="text-white">{icon}</span>}</div>
      </div>
      <p className="text-2xl font-bold font-numeric text-gray-900">{value}</p>
    </div>
  );
}

function EmptyState({ title }: { title: string }) {
  return (
    <div className="text-center py-8 text-gray-400">
      <p className="text-3xl mb-2">📊</p>
      <p className="text-sm">{title}</p>
    </div>
  );
}

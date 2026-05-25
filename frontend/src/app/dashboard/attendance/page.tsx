"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth-store";
import { attendanceApi, type AttendanceSummary, type MonthlyStats } from "@/lib/api/attendance";
import { studentsApi } from "@/lib/api/students";

export default function AttendancePage() {
  const user = useAuthStore((s) => s.user);
  const [studentId, setStudentId] = useState<string | null>(null);
  const [summaries, setSummaries] = useState<AttendanceSummary[]>([]);
  const [stats, setStats] = useState<MonthlyStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const isTeacher = ["TEACHER", "HOD", "ADMIN", "SUPER_ADMIN"].includes(user?.role ?? "");
  const [markStudentId, setMarkStudentId] = useState("");
  const [markSubject, setMarkSubject] = useState("");
  const [markStatus, setMarkStatus] = useState<"PRESENT" | "ABSENT" | "LATE">("PRESENT");
  const [markMsg, setMarkMsg] = useState("");

  const handleMark = async () => {
    if (!markStudentId || !markSubject) {
      setMarkMsg("Student ID and subject ID required.");
      return;
    }
    try {
      await attendanceApi.bulkMark([
        {
          student: markStudentId,
          subject: markSubject,
          status: markStatus,
          date: new Date().toISOString().split("T")[0],
          period: 1,
        },
      ]);
      setMarkMsg("Attendance marked.");
    } catch (e: unknown) {
      setMarkMsg(e instanceof Error ? e.message : "Mark failed.");
    }
  };

  useEffect(() => {
    if (!user?.id) return;

    const fetchData = async () => {
      try {
        setLoading(true);

        // Student role — fetch student profile first
        let sid = user.id;
        if (user.role === "STUDENT") {
          const profileRes = await studentsApi.me();
          sid = profileRes.data.id;
          setStudentId(sid);
        }

        const [summaryRes, statsRes] = await Promise.all([
          attendanceApi.summary({ student: sid }),
          attendanceApi.monthlyStats(sid),
        ]);
        setSummaries(summaryRes.data ?? []);
        setStats(statsRes.data ?? null);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Failed to load attendance.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user?.id, user?.role]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600" />
          <p className="text-sm text-gray-400">Loading attendance...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="m-6 p-5 bg-red-50 border border-red-200 rounded-xl text-red-700 flex items-center gap-3">
        <span className="text-xl">⚠️</span>
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Attendance</h1>
          <p className="text-sm text-gray-500 mt-0.5">Track your class attendance</p>
        </div>
        {stats && (
          <div className={`px-4 py-2 rounded-full text-sm font-semibold ${
            stats.is_low ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"
          }`}>
            {stats.is_low ? "⚠️ Low Attendance" : "✅ Good Standing"}
          </div>
        )}
      </div>

      {isTeacher ? (
        <div className="rounded-xl border border-gray-200 bg-white p-4 space-y-3">
          <p className="text-sm font-semibold text-gray-800">Mark attendance (teacher)</p>
          <div className="grid gap-2 sm:grid-cols-3">
            <input value={markStudentId} onChange={(e) => setMarkStudentId(e.target.value)} placeholder="Student UUID" className="rounded-lg border px-3 py-2 text-sm" />
            <input value={markSubject} onChange={(e) => setMarkSubject(e.target.value)} placeholder="Subject UUID" className="rounded-lg border px-3 py-2 text-sm" />
            <select value={markStatus} onChange={(e) => setMarkStatus(e.target.value as "PRESENT" | "ABSENT" | "LATE")} className="rounded-lg border px-3 py-2 text-sm">
              <option value="PRESENT">Present</option>
              <option value="ABSENT">Absent</option>
              <option value="LATE">Late</option>
            </select>
          </div>
          <button onClick={handleMark} className="rounded-lg bg-accent px-4 py-2 text-sm text-white">Save</button>
          {markMsg ? <p className="text-sm text-gray-600">{markMsg}</p> : null}
        </div>
      ) : null}

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "Total Classes", value: stats.total, color: "blue" },
            { label: "Present", value: stats.present, color: "green" },
            { label: "Absent", value: stats.absent, color: "red" },
            { label: "Late", value: stats.late, color: "yellow" },
          ].map((s) => (
            <StatCard key={s.label} {...s} />
          ))}
        </div>
      )}

      {stats && (
        <div className={`rounded-2xl p-6 border ${
          stats.is_low ? "bg-red-50 border-red-200" : "bg-green-50 border-green-200"
        }`}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-xs uppercase tracking-wide text-gray-500 font-medium">
                Overall Attendance
              </p>
              <p className={`text-5xl font-black mt-1 ${
                stats.is_low ? "text-red-600" : "text-green-600"
              }`}>
                {stats.percentage}%
              </p>
            </div>
            <div className="text-right text-sm text-gray-500 space-y-1">
              <p>{stats.present} present out of {stats.total}</p>
              <p className="text-orange-500 font-medium">75% minimum required</p>
            </div>
          </div>
          <div className="relative bg-gray-200 rounded-full h-4 overflow-hidden">
            <div className="absolute top-0 bottom-0 w-0.5 bg-orange-400 z-10"
              style={{ left: "75%" }} />
            <div
              className={`h-4 rounded-full transition-all duration-700 ${
                stats.is_low ? "bg-red-500" : "bg-green-500"
              }`}
              style={{ width: `${Math.min(stats.percentage, 100)}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-400 mt-1.5">
            <span>0%</span>
            <span className="text-orange-500 font-semibold" style={{ marginLeft: "71%" }}>75%</span>
            <span>100%</span>
          </div>
        </div>
      )}

      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-3">Subject-wise Breakdown</h2>
        {summaries.length === 0 ? (
          <div className="text-center py-16 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
            <p className="text-4xl mb-3">📋</p>
            <p className="text-gray-500 font-medium">No attendance records yet</p>
            <p className="text-gray-400 text-sm mt-1">Records will appear once classes begin</p>
          </div>
        ) : (
          <div className="space-y-3">
            {summaries.map((s) => (
              <SubjectCard key={s.id} summary={s} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: number; color: string }) {
  const styles: Record<string, string> = {
    blue: "bg-blue-50 border-blue-100 text-blue-700",
    green: "bg-green-50 border-green-100 text-green-700",
    red: "bg-red-50 border-red-100 text-red-700",
    yellow: "bg-yellow-50 border-yellow-100 text-yellow-700",
  };
  return (
    <div className={`rounded-xl border p-4 ${styles[color]}`}>
      <p className="text-xs uppercase tracking-wide opacity-60 font-medium">{label}</p>
      <p className="text-3xl font-black font-numeric mt-1">{value}</p>
    </div>
  );
}

function SubjectCard({ summary }: { summary: AttendanceSummary }) {
  const pct = Number(summary.percentage);
  const isLow = pct < 75;
  return (
    <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-800">{summary.subject_name}</h3>
        <span className={`text-sm font-bold px-3 py-1 rounded-full ${
          isLow ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"
        }`}>
          {pct}% {isLow && "⚠️"}
        </span>
      </div>
      <div className="bg-gray-100 rounded-full h-2 mb-3">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${isLow ? "bg-red-400" : "bg-green-400"}`}
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
      <div className="grid grid-cols-4 gap-2 text-xs text-center">
        <div className="bg-gray-50 rounded-lg p-2">
          <p className="text-gray-400">Total</p>
          <p className="font-bold text-gray-700">{summary.total_classes}</p>
        </div>
        <div className="bg-green-50 rounded-lg p-2">
          <p className="text-green-400">Present</p>
          <p className="font-bold text-green-700">{summary.present_count}</p>
        </div>
        <div className="bg-red-50 rounded-lg p-2">
          <p className="text-red-400">Absent</p>
          <p className="font-bold text-red-700">{summary.absent_count}</p>
        </div>
        <div className="bg-yellow-50 rounded-lg p-2">
          <p className="text-yellow-400">Late</p>
          <p className="font-bold text-yellow-700">{summary.late_count}</p>
        </div>
      </div>
    </div>
  );
}
